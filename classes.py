class Node:
    """Class for storing the character-value pairs in graph style i.e. with left and right nodes"""
    def __init__(self, val, freq):
        """Initializes the object with its value and frequency"""
        self.val = val
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        try:
            return self.freq < other.freq
        except:
            return False

    def __str__(self):
        return str((self.val, self.freq))

    def __repr__(self):
        return str((self.val, self.freq))


class Heap:
    """An implementation of Min Heap queue or min priority queue"""
    def __init__(self, l = []):
        """Initializes the object with list l and sorts it"""
        self.l = l
        self.sort()
    
    def _move_down(self, pos):
        """A recursive function for swapping parents with children"""
        item = self.l[pos]
        c1_pos = (pos + 1) * 2
        c2_pos = pos * 2 + 1
        try:
            c1 = self.l[c1_pos]
        except:
            try:
                c2 = self.l[c2_pos]
            except:
                return
            else:
                if item > c2:
                    self.l[pos], self.l[c2_pos] = self.l[c2_pos], self.l[pos]
                    pos = c2_pos
                    self._move_down(pos)
                    return
        else:
            c2 = self.l[c2_pos]
            if c1 > c2:
                if item > c2:
                    self.l[pos], self.l[c2_pos] = self.l[c2_pos], self.l[pos]
                    pos = c2_pos
                    self._move_down(pos)
                    return
            else:
                if item > c1:
                    self.l[pos], self.l[c1_pos] = self.l[c1_pos], self.l[pos]
                    pos = c1_pos
                    self._move_down(pos)
                
    def sort(self):
        """Sorts the heap queue"""
        if len(self.l)%2 == 0:
            if self.l == []:
                return
            ind = len(self.l)-1
            item = self.l[ind]
            parent_pos = ind//2
            parent = self.l[parent_pos]
            if item < parent:
                self.l[ind], self.l[parent_pos] = self.l[parent_pos], self.l[ind]
            ind = ind - 1
        else:
            ind = len(self.l) - 1
        for i in range(ind, -1, -2):
            if i%2 == 0:
                parent_pos = i//2 -1
            else:
                parent_pos = i//2
            if parent_pos < 0:
                break
            self._move_down(parent_pos)

    def push(self, item):
        """Pushes an item into the heap and sorts it"""
        self.l.append(item)
        self.sort()

    def pop(self):
        """Pops the top item from the heap and sorts it"""
        first = self.l[0]
        last = self.l[-1]
        self.l[0], self.l[-1] = last, first
        first = self.l.pop()
        self.sort()
        return first
