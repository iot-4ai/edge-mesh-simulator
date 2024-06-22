from sortedcontainers import SortedDict

class RPQ:

    def __init__(self):
        self.ins = SortedDict()  # (item, time) -> True/False
        self.delmin = SortedDict()  # time -> item
        self.current_time = 0

    def _genkey(self, item, t):
        return (item, t)

    # RETURNS FIRST DELMIN ISSUE
    def insert(self, item, t):
        # Case (i): If t is the present t
        if t >= self.current_time:
            key = self._genkey(item, t)
            self.ins[key] = True
            self.current_time = max(self.current_time, t)
        else:
            # Case (ii): Return the first inconsistent operation
            key = self._genkey(item, t)
            self.ins[key] = True
            for del_time in self.delmin:
                if del_time > t:
                    k = self.delmin[del_time]
                    print(f"Inconsistent Op = {del_time}: {k}")
                    return (k, del_time)
        return None

    # RETURNS MINKEY GREATER THAN RIGHT BEFORE T
    def del_min(self, t):
        t_prime = max([time for time in self.delmin if time > t], default=None)
        if t_prime is not None:
            k = max([time for time in self.delmin if time < t], default=0)
            # Case (ii): del_min at a past time
            # Find the key k' that has been deleted immediately before time t in delmin
            min_key = min([item for item in self.ins if item[1] > k and self.ins[item]],
                default=None)
        else:
            # Case (i): del_min at the most recent time
            min_key = min([item for item in self.ins if self.ins[item]], default=None)
        if min_key is None: return None
        del_item = min_key[0]
        self.delmin[t] = del_item
        self.ins[min_key] = False
        self.current_time = max(self.current_time, t)
        return min_key

    # RETURNS FIRST DELMIN AFTER T
    def revoke_insert(self, t):
        t_prime = min([time for time in self.delmin if time > t], default=None)
        if t_prime is not None:
            print(f"Inconsistent Op = {t_prime}: {self.delmin[t_prime]}")
            return t_prime
        else:  # noqa: RET505
            p = [item for item in self.ins if item[1] == t]
            for i in p:
                self.ins[p[i]] = False
        return None

    # RETURN FIRST DELMIN AFTER T
    def revoke_del_min(self, t):
        t_prime = min([time for time in self.delmin if time > t], default=None)
        if t_prime is not None:
            print(f"Inconsistent Op = {t_prime}: {self.delmin[t_prime]}")
            return t_prime
        else:  # noqa: RET505
            print("HELLO")
            self.insert(self.delmin[t_prime], t)
        return None

    # RETURNS MIN ELEMENT
    def find_min(self, t):
        t_prime = min([time for time in self.delmin if time > t], default=None)
        if t_prime is not None:
            return self.delmin[t_prime]
        else:  # noqa: RET505
            k_prime = max([time for time in self.delmin if time < t], default=None)
            return min([item for item in self.ins if item[1] > k_prime])

    def print(self):
        print("insert tree:")
        for k, v in self.ins.items():
            print(f"  {k}: {'valid' if v else 'invalid'}")
        print("delmin tree:")
        for k, v in self.delmin.items():
            print(f"  {k}: {v}")

def test_RPQ():
    rpq = RPQ()

    # Basic Insertions
    print("R: ", rpq.insert(5, 1))
    print("R: ", rpq.insert(20, 2))
    print("R: ", rpq.insert(15, 3))
    print("After insertions:")
    rpq.print()

    # Basic Deletions
    print("R: ", rpq.del_min(4))
    print("After first del_min:")
    rpq.print()

    print("R: ", rpq.del_min(5))
    print("After second del_min:")
    rpq.print()

    # Retroactive Insertions
    print("Retroactive insertions:")
    print("R: ", rpq.insert(25, 2))
    rpq.print()

    # Retroactive del_min
    print("Retroactive del_min:")
    print("R: ", rpq.del_min(3))
    rpq.print()

    # Revoke Insertions
    print("Revoke insertion:")
    print("R: ", rpq.revoke_insert(1))
    rpq.print()

    # Revoke del_min
    print("Revoke del_min:")
    print("R: ", rpq.revoke_del_min(4))
    rpq.print()

    # Complex Scenario
    print("Complex scenario:")
    print("R: ", rpq.insert(30, 6))
    rpq.print()
    print("R: ", rpq.del_min(7))
    rpq.print()
    print("R: ", rpq.revoke_del_min(5))
    rpq.print()
    print("R: ", rpq.revoke_insert(2))
    rpq.print()

test_RPQ()
