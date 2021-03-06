#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import re


def is_normal(filename):
	with open(filename,'r') as f:
		lines = f.readlines()
		if 'Normal termination' in lines[-1]:
			return True
		else:
			return False

def dump_gjf(filename,elem,xyz, charge,mem='2GB',method='#M062X/6-311+G(2df,2p)'):
	sum_charge = sum(charge)
	#print(filename,charge,int(sum_charge))
	chk = filename.split('/')[-1].split('.')[0]+'.chk'
	with open(filename,'w') as f:
		f.write('%mem={}\n'.format(mem))
		f.write('%chk={}\n'.format(chk))
		f.write('{}\n'.format(method))
		f.write('\n')
		f.write('Generated by Qiang @G303 Nanjing\n')
		f.write('\n')
		f.write('{} {}\n'.format(round(sum_charge),1))
		for i,x in enumerate(elem):
			f.write('{:4s}\t {:12.8f}\t {:12.8f} \t{:12.8f}\n'.format(elem[i],xyz[i][0],xyz[i][1],xyz[i][2]))
		f.write('\n')
		f.write('\n')



def load_gau(filename,prop):
	"""
	input:  
		- the filename of GAUSSIAN 16 (test)
	output:
		- xyz (in the unit of angstrom)
		- charge,q	(in the unit of e)
	"""
	if prop == 'xyz':
		xyzs = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if 'Standard orientation' in line:
							idx = []
							xyz = []
							# skip the lines
							# ---------------------------------------------------------------------
							# Center     Atomic      Atomic             Coordinates (Angstroms)
							# Number     Number       Type             X           Y           Z
							# ---------------------------------------------------------------------
							for i in range(4):
								line = f.readline()
							for i in range(999):
								line = f.readline()
								if '-------' in line:
									xyzs.append(xyz)
									break
								else:
									data = line.split()
									#print(data)
									idx.append(int(data[1]))
									xyz.append([float(data[3]),float(data[4]),float(data[5])])
		else:
			print('Not Terminated Normally!')
		#print(idx)
		return idx, xyzs[-1]
	elif prop=='charge':
		elems = []
		qs = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if 'Mulliken atomic charges:' in line:
							elem = []
							q = []
							# skip the line
							#             1
							line = f.readline()
							for i in range(999):
								line = f.readline()
								if 'Sum of Mulliken atomic charges' in line:
									qs.append(q)
									elems.append(elem)
									break
								else:
									data = line.split()
		#							print(data)
									elem.append(str(data[1]))
									q.append(float(data[2]))
		else:
			print('Not Terminated Normally!')
		return elems[-1],qs[-1]
	
	elif prop=='dipole':
		dipoles = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if 'Dipole moment' in line:
							line = f.readline()
							dipole = [float(line.split()[1]), float(line.split()[3]), float(line.split()[5]),float(line.split()[7])]
							dipoles.append(dipole)
		return dipoles[-1]

	elif prop=='orbit':
		HOMOS = []
		LUMOS = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if 'The electronic state is ' in line:
							HOMO = []
							LUMO = []
							for i in range(100000):
								line = f.readline()
								if 'Alpha  occ. eigenvalues' in line:
									data0 = line[28:38].strip()
									data1 = line[38:48].strip()
									data2 = line[48:58].strip()
									data3 = line[58:68].strip()
									data4 = line[68:78].strip()
									#data = [float(x) for x in line.split('--')[1].split()]
									if len(data0)>0:
										HOMO.append(float(data0))
									if len(data1)>0:
										HOMO.append(float(data1))
									if len(data2)>0:
										HOMO.append(float(data2))
									if len(data3)>0:
										HOMO.append(float(data3))
									if len(data4)>0:
										HOMO.append(float(data4))
									#HOMO.extend(data)
									#print(HOMO)
								elif 'Alpha virt. eigenvalues' in line:
									data0 = line[28:38].strip()
									data1 = line[38:48].strip()
									data2 = line[48:58].strip()
									data3 = line[58:68].strip()
									data4 = line[68:78].strip()
									#print(len(data0))
									if len(data0)>0:
										LUMO.append(float(data0))
									if len(data1)>0:
										LUMO.append(float(data1))
									if len(data2)>0:
										LUMO.append(float(data2))
									if len(data3)>0:
										LUMO.append(float(data3))
									if len(data4)>0:
										LUMO.append(float(data4))
									#data = [float(x) for x in line.split('--')[1].split()]
									#LUMO.extend(data)
								else:
									HOMOS.append(HOMO)
									LUMOS.append(LUMO)
									break
			return HOMOS[-1],LUMOS[-1]
		else:
			print('Not Normal Terminated!')

	elif prop=='E':
		SCFs = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if 'SCF Done:' in line:
							SCF = float(line.split()[4])
							SCFs.append(SCF)
			return SCFs[-1]
		else:
			print('Not Normal Terminated!')
		
	elif prop=='entropy' or prop=='S':
		E_ = []
		Cv_ = []
		S_ = []
		if is_normal(filename):
			with open(filename,'r') as f:
				while True:
					line = f.readline()
					if not line:
						break
					else:
						if '                    E (Thermal)             CV                S' in line:
							# skip the unit line: KCal/Mol        Cal/Mol-Kelvin    Cal/Mol-Kelvin
							line = f.readline()
							for x in range(5):
								line = f.readline()
								E_.append(float(line.split()[1]))
								Cv_.append(float(line.split()[2]))
								S_.append(float(line.split()[3]))
			# order:
			#		Total -> Elec -> Trans -> Rot -> Vib
			return E_, Cv_, S_
		else:
			print('Not Normal Terminated!')

		#print(xyzs[-1])
		#print(qs)
		#if len(xyzs) >1:
		#	return np.array(idx),np.array(xyzs[-1]), np.array(qs[-1])
		#else:
		#	return np.array(idx), np.array(xyzs), np.array(qs)
	#return np.array(idx), np.array(xyzs[-1]), np.array(qs[-1])


if __name__ == '__main__':
	# section for counting the elements
	import glob as glob
#	from collections import Counter
#	outs = glob.glob('../*.out')
#	#print(outs)
#	indexes = []
#	for out in outs:
#		idx, xyz = load_gau(out,'xyz')
#		indexes.extend(idx)
#	results = Counter(indexes)
#	print(results)

#	# section for generating the gjf
#	outs = glob.glob('../OPT/*.out')
#	for out in outs:
#		idx, xyz = load_gau(out,'xyz')
#		elem, q = load_gau(out,'charge')
#		outname = out.split('/')[-1].split('.')[0]+'.gjf'
#		dump_gjf(outname,elem, xyz, q)

	#out = '../../211201_vacuum_opt/OPT/121-69-7.out'
	out = '../Energy/131-53-3.out'
	HOMO, LUMO = load_gau(out,'orbit')
	dipole = load_gau(out,'dipole')
	elem, charge = load_gau(out,'charge')
	print(HOMO)
	#print(elem,charge)
	#print(dipole)
	
#	print(HOMO)
