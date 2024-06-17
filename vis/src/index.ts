import * as THREE from 'three';
import {KeyboardKeyHold as KHold, } from "hold-event";
import CameraControls from 'camera-controls';
import axios from "axios";
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
CameraControls.install( { THREE: THREE } );

let width = window.innerWidth, height = window.innerHeight;
const cLight = new THREE.Color(0xDFA878), cDark = new THREE.Color(0xBA704F)
const clock = new THREE.Clock(), scene = new THREE.Scene();
scene.background = cLight;
let delta: number
let camera: THREE.OrthographicCamera, 
    cameraControls: CameraControls,
    factoryGroup: THREE.Group,
    controllers: Array<Controller>
let grid: THREE.Mesh,
    factorySize: THREE.Vector3 = new THREE.Vector3(),
    center: THREE.Vector3 = new THREE.Vector3()
let dummyMat: THREE.Matrix4 = new THREE.Matrix4()
const renderer = new THREE.WebGLRenderer(); renderer.setSize( width, height );
const sceneUrl = './assets/scene-1.glb';
const gltfLoader = new GLTFLoader();
document.body.appendChild( renderer.domElement );

interface Controller {
    name: string;
    comm: string;
    pos: { x: number; y: number; z: number };
    orient: { roll: number; pitch: number; yaw: number };
    ip: string;
    signal: number;
}

// -------------------------------------------------------------------------------
// KEY STUFF
const KEYCODE = {
	W: 87, A: 65, S: 83, D: 68,
	ARROW_LEFT: 37, ARROW_UP: 38, ARROW_RIGHT: 39, ARROW_DOWN: 40,
    R: 82,
    G: 71,
    H: 72,
    ONE: 49
};
const wKey = new KHold( KEYCODE.W, 16.666 ), aKey = new KHold( KEYCODE.A, 16.666 ), sKey = new KHold( KEYCODE.S, 16.666 ), dKey = new KHold( KEYCODE.D, 16.666 );
aKey.addEventListener( 'holding', function( event:any ) { cameraControls.truck( - 0.05 * event.deltaTime, 0, false ) } );
dKey.addEventListener( 'holding', function( event:any ) { cameraControls.truck(   0.05 * event.deltaTime, 0, false ) } );
wKey.addEventListener( 'holding', function( event:any ) { cameraControls.forward(   0.05 * event.deltaTime, false ) } );
sKey.addEventListener( 'holding', function( event:any ) { cameraControls.forward( - 0.05 * event.deltaTime, false ) } );

const leftKey  = new KHold( KEYCODE.ARROW_LEFT,  100 ), rightKey = new KHold( KEYCODE.ARROW_RIGHT, 100 ), upKey    = new KHold( KEYCODE.ARROW_UP,    100 ), downKey  = new KHold( KEYCODE.ARROW_DOWN,  100 );
leftKey.addEventListener ( 'holding', function( event:any ) { cameraControls.rotate( - 0.1 * THREE.MathUtils.DEG2RAD * event.deltaTime, 0, true ) } );
rightKey.addEventListener( 'holding', function( event:any ) { cameraControls.rotate(   0.1 * THREE.MathUtils.DEG2RAD * event.deltaTime, 0, true ) } );
upKey.addEventListener   ( 'holding', function( event:any ) { cameraControls.rotate( 0, - 0.05 * THREE.MathUtils.DEG2RAD * event.deltaTime, true ) } );
downKey.addEventListener ( 'holding', function( event:any ) { cameraControls.rotate( 0,   0.05 * THREE.MathUtils.DEG2RAD * event.deltaTime, true ) } );

const rKey = new KHold( KEYCODE.R, 16.666 ), gKey = new KHold( KEYCODE.G, 16.666 ), hKey = new KHold( KEYCODE.H, 16.666 ), oneKey = new KHold( KEYCODE.ONE, 16.666 );
rKey.addEventListener( 'holdStart', function() { 
    cameraControls.setLookAt(0,center.y,center.z + 100,center.x,0,center.z,true);
    cameraControls.zoomTo(fzoom()); 
}); 
gKey.addEventListener( 'holdEnd', function() { grid.visible = !grid.visible }); 
hKey.addEventListener( 'holdEnd', function() { factoryGroup.visible = !factoryGroup.visible }); 
oneKey.addEventListener( 'holdStart', function() { 
    cameraControls.setLookAt(center.x,center.y+60,center.z,center.x,center.y,center.z,true); cameraControls.rotateTo(Math.PI/2, 0, true);
    cameraControls.zoomTo(fzoom(),true);
}); 
function onWindowResize() {
    width = window.innerWidth;
    height = window.innerHeight;
    renderer.setSize(width, height);
    camera.left = width / -200; camera.right = width / 200; camera.top = height / 200; camera.bottom = height / -200;
    camera.updateProjectionMatrix();
    cameraControls.zoomTo(fzoom(),true);
}
function fzoom() { return (width / height) / 10; }
window.addEventListener('resize', onWindowResize);
// -------------------------------------------------------------------------------

init()
anim()

async function reqControllers() {
    try {
        const response = await axios.get('http://localhost:8000/controllers'); 
        return response.data; 
    } catch (error) {
        console.error('Error fetching data:', error);
        return [];
    }
}

async function getControllers() {
    const data = await reqControllers(); 
    return data.map((item: any): Controller => ({
        name: item.name, comm: item.comm, pos: item.pos, orient: item.orient, ip: item.ip, signal: item.signal,
    }));
}


function initCamera() {
    camera = new THREE.OrthographicCamera( width / -200, width / 200, height / 200, height / -200, 0.1, 3000 );
    camera.position.set( 0, 20, 100);
    cameraControls = new CameraControls( camera, renderer.domElement );
    cameraControls.zoomTo(fzoom());
}

function loadFactory() {
    gltfLoader.load(
        sceneUrl,
        (gltf: any) => {
            factoryGroup = gltf.scene;
            // DASHED BOX
            const tempBox = new THREE.BoxHelper(factoryGroup, 0xffffff); 
            const line = new THREE.Line( tempBox.geometry.toNonIndexed(), 
                new THREE.LineDashedMaterial({ color: 0xffffff, dashSize: 1, gapSize: 0.5 }));
            line.computeLineDistances();
            line.applyMatrix4(tempBox.matrix);

            factoryGroup.traverse((child: any) => {
                if (child instanceof THREE.Mesh) {
                    child.castShadow = child.receiveShadow = true;
                    if (child.name == "Walls") factoryGroup.remove(child)
                }
            });
            factoryGroup.add(line)
            factoryGroup.position.set(-20,0,10)

            // ADD BOUNDING BOX
            const boundingBox = new THREE.Box3().setFromObject(factoryGroup);
            boundingBox.getSize(factorySize);
            boundingBox.getCenter(center);
            cameraControls.setPosition(0, center.y, center.z + 100)
            scene.add(factoryGroup);

            // GRID
            const width = factorySize.z+2, height = factorySize.x+2
            const gridGeometry = new THREE.PlaneGeometry(width, height, width, height);
            const gridMaterial = new THREE.MeshBasicMaterial({ color: cDark});
            grid = new THREE.Mesh(gridGeometry, gridMaterial);
            grid.rotation.x = -Math.PI / 2; 
            grid.rotation.z = Math.PI/ 2;
            grid.visible = false;
            scene.add(grid);
        },
        undefined,
        (error: any) => {
            console.error('An error happened while loading the GLTF model', error);
        }
    );
    
}
 
async function init() {
    initCamera()
    loadFactory()

    {
        controllers = await getControllers();
        console.log(controllers)
        const boxGeometry = new THREE.BoxGeometry(0.8, 0.8, 0.8);
        const material = new THREE.MeshBasicMaterial({ color: 0x0047AB });
        const mesh = new THREE.InstancedMesh(boxGeometry, material, controllers.length);
        let index = 0;
        controllers.forEach((item: Controller) => {
            dummyMat.setPosition(item.pos.x+0.5,item.pos.z + 0.5,-item.pos.y + 0.5);
            mesh.setMatrixAt(index, dummyMat);
            index++;
        });
        mesh.position.set(-20,0,10)
        scene.add(mesh);
    }

    scene.add(new THREE.AmbientLight(0x2d3645, 8));
    let directionalLight = new THREE.DirectionalLight(0xffffff, 4.5);
    directionalLight.position.set(-50, 50, -50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.set(4000, 4000);
    scene.add(directionalLight);

    renderer.render( scene, camera );
}
function anim () {
    requestAnimationFrame( anim );
	delta = clock.getDelta();
	cameraControls.update( delta );

	renderer.render( scene, camera );
};

