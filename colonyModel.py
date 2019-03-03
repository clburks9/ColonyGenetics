"""
***********************************************************
File: colonyModel.py
Author: Luke Burks
Date: March 2019

Implements a model for visulaization of recessive trait 
spread among small colonys of space travelers
***********************************************************
"""


__author__ = "Luke Burks"
__copyright__ = "Copyright 2019"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Luke Burks"
__email__ = "clburks9@gmail.com"
__status__ = "Development"


import numpy as np;


class Colonist:


	def __init__(self,ident=None,gene = None, via = None, ty = None,viaRule = [1,1,1]):

		if(ident is None):
			self.id = np.random.randint(0,1000000); 
		else:
			self.id = ident; 

		if(gene is None):
			self.gene = [np.random.randint(0,2),np.random.randint(0,2)]; 
		else:
			self.gene = gene;

		if(via is None):
			#self.viability = np.random.random()
			g = self.gene; 
			if(g[0] == 0 and g[1] == 0):
				self.viability = viaRule[0]; 
			elif((g[0] == 0 and g[1] == 1) or (g[0] == 1 and g[1] == 0)):
				self.viability = viaRule[1]; 
			elif(g[0] == 1 and g[1] == 1):
				self.viability = viaRule[2]; 

		else:
			self.viability = via; 

		if(ty is None):
			self.type = np.random.randint(0,2);
		else:
			self.type = ty; 

	def display(self):
		print("Colonist ID: {}".format(self.id)); 
		print("    Viability: {}".format(self.viability)); 
		print("    Type: {}".format(self.type)); 
		print("    Gene: {}".format(self.gene)); 


class Colony:


	#persSet encodes how likely each outcome is to exist in the initial popultation
	def __init__(self,N=10,persSet = [.2,.8],viaRule = [1,1,1]):
		self.members = []; 

		self.popCounter = 0; 

		self.viaRule = viaRule; 
		self.persSet = persSet; 

		for i in range(0,N):
			t = np.random.choice([0,1],size=2,p=self.persSet).tolist()
			self.members.append(Colonist(ident=self.popCounter,gene=t,viaRule = self.viaRule)); 
			self.popCounter+=1; 


	def __getitem__(self,key):
		return self.members[key]; 


	def getGenes(self):
		allgenes = []; 
		for m in self:
			allgenes.append(m.gene); 
		return allgenes; 


	def getViability(self):
		allVia = []; 
		for m in self:
			allVia.append(m.viability); 
		return allVia; 


	def modViability(self,viaRule):
		self.viaRule = viaRule
		for c in self:
			g = c.gene; 
			if(g[0] == 0 and g[1] == 0):
				c.viability = self.viaRule[0]; 
			elif((g[0] == 0 and g[1] == 1) or (g[0] == 1 and g[1] == 0)):
				c.viability = self.viaRule[1]; 
			elif(g[0] == 1 and g[1] == 1):
				c.viability = self.viaRule[2]; 


	def getTypes(self):
		allTypes = []; 
		for m in self.members:
			allTypes.append(m.type); 
		return allTypes; 

	def size(self):
		return len(self.members); 

	def choosePair(self):
		
		#get indexes of all type 0 and type 1
		zeros =  []; 
		ones = []; 
		for i in range(0,self.size()):
			if(self[i].type == 0):
				zeros.append(i); 
			elif(self[i].type == 1):
				ones.append(i); 

		#randomly choose from them weighted by viability
		allVias = np.array(self.getViability()); 
		zeroVia = allVias[zeros]; 
		oneVia = allVias[ones]; 

		zeroVia = zeroVia/sum(zeroVia); 
		oneVia = oneVia/sum(oneVia); 

		a = np.random.choice(zeros,p=zeroVia); 
		b = np.random.choice(ones,p=oneVia);

		return [self[a],self[b]]; 


	def breed(self,pair):

		#take a random index of each trait and combine them
		t = []; 
		t.append(np.random.choice(pair[0].gene)); 
		t.append(np.random.choice(pair[1].gene)); 

		c = Colonist(ident=self.popCounter,gene = t,viaRule=self.viaRule); 
		self.popCounter+=1; 

		return c; 

	def update(self):

		newGen = []; 
		while(len(newGen) < self.size()):
			c = self.breed(self.choosePair()); 
			newGen.append(c); 
		self.members = newGen; 

if __name__ == '__main__':
	
	a = Colony(); 
	b = a.breed(a.choosePair()); 
	b.display();





