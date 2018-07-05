import pickle
import os
from classes import Heap, Node
        
class Huffman:
    """An implementation of the Huffman Algorithm for text compression"""
    def __init__(self, out_path, in_path, g_path):
        """Takes the output path, input path and graph path for the input file, output file and the graph file"""
        self.out_path = out_path
        self.in_path = in_path
        self.g_path = g_path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
    
    def freq_dict(self, text):
        """Takes a string text and returns a dictionary with the character-frequency pairs of all characters in the text"""
        freq = {}
        for char in text:
            if not char in freq:
                freq[char] = 0
            freq[char] += 1
        return freq
    
    def heap_list(self, freq):
        """Takes a character-frequency dictionary, converts them into Nodes and sorts them into a heap"""
        for key in freq:
            node = Node(key, freq[key])
            self.heap.append(node)
        self.heap = Heap(self.heap)
        self.heap.sort()

    def create_graph(self):
        """Creates a Huffman graph from self.heap"""
        while(len(self.heap.l) > 1):
            node1 = self.heap.pop()
            node2 = self.heap.pop()
            merged = Node(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            self.heap.push(merged)

    def _make_codes_recur(self, node, code):
        """Recursive function for mapping digits to characters"""
        if node == None:
            return
            
        if node.val != None:
            self.codes[node.val] = code
            self.reverse_mapping[code] = node.val
            return

        self._make_codes_recur(node.left, code + "0")
        self._make_codes_recur(node.right, code + "1")

    def make_code(self):
        """Creates the character-code and vice-versa dictionaries"""
        self.node = self.heap.pop()
        code = ""
        self._make_codes_recur(self.node, code)

    def encode_text(self, text):
        """Encodes the text using the coded values in self.codes"""
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text
    
    def pad_text(self, text):
        """Pads the encoded text with 0's to make it complete bytes of data"""
        extra = 8 - len(text)%8
        for i in range(extra):
            text += "0"
        info = "{0:08b}".format(extra)
        text = info + text
        return text

    def byte_array(self, text):
        """Creates a byte array out of the padded text"""
        b = bytearray()
        for i in range(0, len(text), 8):
            byte = text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self):
        """Compresses the text from the input file to the output file and creates a graph used for decompression"""
        with open(self.in_path) as f, open(self.out_path, "wb") as o, open(self.g_path, "wb") as g:
            text = f.read().rstrip()
            freq = self.freq_dict(text)
            self.heap_list(freq)
            self.create_graph()
            self.make_code()
            encoded_text = self.encode_text(text)
            padded_encoded_text = self.pad_text(encoded_text)
            b = self.byte_array(padded_encoded_text)
            o.write(bytes(b))
            pickle.dump(self.node, g)
        print("Compressed")

    def depad_text(self, bit_text):
        """Removes the padding from the binary text strings"""
        added_zeros = int(bit_text[:8], 2)
        return bit_text[8:-added_zeros]

    def decode_text(self, depadded_text):
        """Moves through the graph to find characters from the depadded text"""
        decoded_text = ""
        main_node = self.node
        current_node = self.node
        for bit in depadded_text:
            if bit == "0":
                new_node = current_node.left
            elif bit == "1":
                new_node = current_node.right
            if new_node.val != None:
                decoded_text += new_node.val
                current_node = main_node
            else:
                current_node = new_node
        return decoded_text

    def decompress(self):
        """Decompresses the data in the input file to the output file using the graph file as a table"""
        with open(self.in_path, "rb") as f, open(self.out_path, "w") as o, open(self.g_path, "rb") as g:
            self.node = pickle.load(g)
            bit_text = ""
            byte = f.read(1)
            while(byte != b""):
                
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, "0")
                bit_text += bits
                byte = f.read(1)
            
            depadded_text = self.depad_text(bit_text)
            decoded_text = self.decode_text(depadded_text)
            o.write(decoded_text)
        print("Decompressed")

compressor = Huffman(out_path = "compressed.bin", in_path = "original.txt", g_path = "graph.hmap")
compressor.compress()

in_size = os.path.getsize("original.txt")
out_size = os.path.getsize("compressed.bin")
graph_size = os.path.getsize("graph.hmap")

compression = 100 - (((out_size + graph_size)/in_size) * 100)
print("Compression Percentage: ", compression, "%", sep = "")
ratio = in_size/(out_size + graph_size)
print("Compression Ratio: ", round(ratio, 3),": 1")

decompressor = Huffman(out_path = "decompressed.txt", in_path = "compressed.bin", g_path = "graph.hmap")
decompressor.decompress()