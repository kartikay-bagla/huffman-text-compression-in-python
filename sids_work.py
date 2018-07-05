from pickle import dump, load
import os

class Huffman_Encoding:
	"""The Main class for encoding"""
	def __init__(self, infile, outfile, treefile):
		"""Takes the input file, output file and the file 
		   for storing the Huffman graph."""
		self.infile = infile
		self.outfile = outfile
		self.treefile = treefile
		self._letter_mapping={}
	
	def _freq_list_create(self):
		"""Creates a list of frequencies for all the characters in the corpus"""
		freqs={}
		self.seq=open(self.infile).read() #Load the data from the infile

		for char in self.seq:
			#if the character has already been observed before, 
			#increment its count in the dictionary
			if char in freqs: freqs[char]+=1 

			#if a new character is found, place it in the 
			#dictionary with an initial count of 1
			else: freqs[char]=1
		
		#Add (freq,char) pairs to freq_lst
		self._freq_lst=[(freqs[x],x) for x in freqs]
		#Sort the freq_lst based on the frequency 
		#of the characters, in reverse order.
		self._freq_lst.sort(key=lambda x: x[0],reverse=True)

	def _generate_tree(self):
		"""Generates the tree from the frequency list"""
		try:
			#Pop out the last two elements from the list as 
			# the left and right child nodes
			l,r=self._freq_lst.pop(), self._freq_lst.pop()

			#Temp stores the new node with the sum of the frequencies 
			# of the child nodes as its frequency, and the corresponding 
			# value as a tuple containing the characters of the child nodes.
			temp=(l[0]+r[0], (l[1],r[1]))

			index=0
			#Try-except block to place temp at the right index 
			# with respect to the frequency
			try:
				while temp[0]<self._freq_lst[index][0]: index+=1
				self._freq_lst.insert(index,temp)
			except IndexError: self._freq_lst.append(temp)
			
			#Recursively call generate_tree with the now modified self.tree
			self._generate_tree()
		
		#Exception is used to end the recursion and return the tree
		# with the child nodes (which were popped out during the 
		# current call but not made into a node) re-added
		except: self._freq_lst.extend([l,r])
		
		#Remove the frequency of the elements to store the tree 
		# comprising of only characters 
		self.tree=[x[1] for x in self._freq_lst]

	def _get_codes(self, lst, string=''):
		"""Creates the dictionary with {character: binary value} pairs"""
		for x in range(2):
			if type(lst[x]) is str:
				# Type = str implies that lst[x] is a leaf node
				self._letter_mapping[lst[x]]=string+str(x)
			else:
				#Type = tuple implies that lst[x] branches out further, 
				# hence not providing a character
				# Get_codes is thus recursively called with lst[x] instead of lst 
				# and a 0 or a 1 added to the current string to signify 
				# the left or right node.
				self._get_codes(lst[x], string+str(x))

	def _text_to_bin(self):
		"""Converts the text into a string of binary 
		   digits according to the letter mapping"""

		#Takes the binary string of each character in the text 
		#and joins them to form the binary string
		return "".join([self._letter_mapping[char] for char in self.seq])
	
	def _pad_bin_text(self, bin_text):
		"""Pads the binary string with 0s so as to get a string perfectly divisible by 8.
			Also appends the number of 0s added to the front of string as binary."""
		
		extra = 8 - len(bin_text)%8 #No of extra zeros to be added
		extra_text = "0" * extra 
		bin_text += extra_text
		#Adding the number of zeros as binary to the beginning of the file
		info = "{0:08b}".format(extra)
		bin_text = info + bin_text
		return bin_text

	def _byte_array(self, pad_bin_text):
		"""Converts the binary string into bytes"""
		b = bytearray()

		#Takes 8 binary string digits at a time and 
		#converts them into bytes
		for i in range(0, len(pad_bin_text), 8):
			byte = pad_bin_text[i : i + 8]
			b.append(int(byte, 2))
		return b

	def compress(self):
		"""Compresses the infile to outfile and 
		creates the treefile to be used for decompression"""

		self._freq_list_create() 	#Create frequency list
		self._generate_tree() 		#Create the Huffman tree
		self._get_codes(self.tree)	#Create the mapping for each character

		#Gets the list of bytes from the text
		byte_array = self._byte_array(self._pad_bin_text(self._text_to_bin()))

		#Writes the data to the outfile and treefile
		with open(self.outfile, "wb") as w, open(self.treefile, "wb") as t:
			w.write(bytes(byte_array))
			dump(self.tree, t)
		print("Compressed")
		
	def _depad_text(self, bit_text):
		"""Remove the trailing zeros added during padding by 
		getting the number of zeros as the first integer in the text"""

		#Gets the number of zeros added from the beginning of the file
		added_zeros = int(bit_text[:8], 2)
		return bit_text[8: - added_zeros]

	def _decode_text(self, depadded_text):
		"""Decodes the depadded text using the treefile"""

		temp=self.tree
		output = ""

		for char in [int(x) for x in depadded_text]:
		
			if type(temp[char]) is str:	
				#If the corresponding node in the tree 
				#is a string, add it to the output string
				output+=temp[char]
				temp=self.tree
			else:
				#Reassign the node to its child node
				temp=temp[char]
		return output

	def decompress(self):
		"""Decompresses the infile to the outfile using the treefile"""
		with open(self.infile, "rb") as f, open(self.outfile, "w") as w, open(self.treefile, "rb") as t:
			self.tree = load(t)
			bit_text = ""

			#Read the bytes from the compressed file
			byte = f.read(1)
			while(byte != b""):
				byte = ord(byte)
				bits = bin(byte)[2:].rjust(8, "0")
				bit_text += bits
				byte = f.read(1)

			depadded_text = self._depad_text(bit_text) #Depad the text by removing the trailing zeros
			decoded_text = self._decode_text(depadded_text)	#Decode the depadded text
			w.write(decoded_text) #Write the output to a file
		print("Decompresed")

compressor = Huffman_Encoding("file.txt", "compressed.bin", "treefile.tree")
compressor.compress()

decompressor = Huffman_Encoding("compressed.bin", "decompressed.txt", "treefile.tree")
decompressor.decompress()
