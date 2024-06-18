#!/bin/bash
cleanup() {
    echo
    lsof -i tcp:8000 | awk 'NR!=1 {print $2}' | xargs kill > /dev/null 2>&1
    lsof -i tcp:5173 | awk 'NR!=1 {print $2}' | xargs kill > /dev/null 2>&1
    sleep 0.1
}
trap cleanup SIGINT

python3 main.py &
cd vis
npm run dev &

wait