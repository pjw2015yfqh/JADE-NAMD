#! /usr/bin/env python
import os
from os import system
#import pybel
import numpy as np
#import coord_lan
import shutil
import time 
import os.path  
import sub_merge_traj_info as merge
import sub_ener_state_cutoff as es_cutoff
import sub_split_coord as split
import sub_inp_json as json
'''
To run this script, you should install openbabel and its python library firstly. 
In linux, the installation command is:
apt-get (or yum) install openbabel (or openbabel.x86_64)
apt-get (or yum) install python-openbabel (or python-openbabel.x86_64)
'''
# lixs 2016.11.2
# The energy gap and the state remain unchanged was taken into account


 
class select_coord():
    def __init__(self):
        inp = json.read_dat()
        self.inp = inp
        self.dim = {}
        self.n_freq = int(inp['n_freq'])
        self.n_select =int(inp['n_select'])
        self.n_traj = int(inp['n_traj'])
        self.filename = inp['filename']
        self.model = []
        self.n_atom = int(inp['n_atom'])
        self.num = 0
        self.Total_E_change = float(inp['Energy_judge'])
        self.Time_after_jump_back = float(inp['State_judge'])
        self.n_ci = int(inp['n_ci'])
        self.n_s0 = int(inp['n_s0'])
        self.savelist = [[0]*3 for i in range(self.n_traj*self.n_select + self.n_ci +self.n_s0 )]  
        self.list_file = 'list_file_save.dat'
        self.main_path = os.getcwd()
    def __rd_xyz_nmol(self):
         """ read how many mol in the xyz file"""
         filename = self.filename
 
         fpin = open(filename, "r")
         nmol = 0
         # read number of atom
         line = fpin.readline()
         while line.strip() != "":
             natom = int(line.split()[0])
             line = fpin.readline()
             # read a mol
             for i in range(natom):
                 line = fpin.readline()
             nmol = nmol + 1
 
             line = fpin.readline()
         fpin.close()
 
         self.dim['n_mol'] = nmol
 
         return
    def read_xyz(self):
        """ read in xyz format in ang """
        n_mol = self.dim['n_mol']

        filename = self.filename
        fpin = open(filename, "r")

        model = []
        for i in xrange(n_mol):
            # number of atom, 
            line = fpin.readline()
            natom = int(line)
            line = fpin.readline()[0:-1]
            molinfo = {'n_atom': natom, 'title':line}

            atom = []
            for j in range(natom):
                line = fpin.readline()
                rec = line.split()
                atomname, x, y, z= rec[0:4]
                record = {'name': atomname, 'coord': [float(x),float(y),float(z)]}
                atom.append(record)
            mol = {'info':molinfo, 'atoms':atom}
            model.append(mol)
        fpin.close()

        self.model = model
        return
    def write_xyz_single(self,iv,id):
        """ write xyz in angstrom unit """
        self.read_xyz()
        savelist = self.savelist
        n_freq = self.n_freq
        filename = "sample.xyz_" + str(id+1)
        savelist[self.num][0] = int(iv+1)
        savelist[self.num][1] = int(id+1)
        savelist[self.num][2] = int(self.num+1)
        self.num = self.num +1


        fp = open(filename, "w")
        nd = id * n_freq
        mol = self.model[nd]
        molinfo = mol['info']
        atoms = mol['atoms']
        n_atom = molinfo['n_atom']
        title = molinfo['title']
        print >>fp, "%d" % (n_atom-19)
        print >>fp, "%s" % title
        for rec in atoms:
            if rec['name'] != 'H':

                coord = rec['coord']
                atom_name = rec['name']
                print >>fp, "%s%15.8f%15.8f%15.8f" % (atom_name,
                                                      coord[0],
                                                      coord[1],
                                                      coord[2])
        fp.close()

        return

    def ener_state_cutoff (self,n_atom,Total_E_change,Time_after_jump_back,i) :
 
        merge.singl_traj(i)
        cutoff = es_cutoff.make(n_atom,Total_E_change,Time_after_jump_back)
        return cutoff

    def select_coord_single_traj(self,id):

        self.__rd_xyz_nmol()
        n_freq = self.n_freq
        n_select = self.n_select 
        nmol = self.dim['n_mol']
        n_atom = self.n_atom
        Total_E_change = self.Total_E_change
        Time_after_jump_back =  self.Time_after_jump_back 
        
        if Total_E_change != 1000 or Time_after_jump_back != 1000:
            nmol = self.ener_state_cutoff(n_atom,Total_E_change,Time_after_jump_back,id)
        
        if nmol/n_freq < n_select :
            n_select = int(nmol/n_freq)

        print "The select geom in the %i file is %i" % (id+1, n_select)
        for i in range(n_select):
            self.write_xyz_single(id,i)


    def select_coord_many(self):
        n_traj = self.n_traj
        curr_path = os.getcwd()
        for i in range(n_traj):
            workdir = curr_path + '/' +  str(i+1) 
            os.chdir(workdir)
            tmp = 0
            for parentdir,dirname,filenames in os.walk(workdir):
                for filename in filenames:  
                     if os.path.splitext(filename)[0]=='sample':  
                         tmp = tmp +1
            if tmp != 0:
                command = "rm -r sample.xyz_*"
                os.system(command)
            try:
                self.select_coord_single_traj(i)
            except:
                continue
        os.chdir(curr_path)

    def copy_s0(self):
        curr_path = os.getcwd()
        s0_path = curr_path + '/0'
        all_path = curr_path + "/all"
        os.chdir(s0_path)
        command = 'cp s0.xyz input.xyz'
        os.system(command)
        split.make()
        command = 'cp all_sample* ' + all_path
        os.system(command)
        for i in range(self.n_s0):
            self.savelist[i][0] = 0
            self.savelist[i][1] = int(i+1)
            self.savelist[i][2] = int(self.num+1)
            self.num = self.num +1
        os.chdir(curr_path)
        print "The select geom in the 0 file is %i" % self.n_s0
                    
    def copy (self) :
        curr_path = os.getcwd()
        all_path = curr_path + "/all"
        num = self.num
        sl = self.savelist
        for nu in range(num):
            if sl[nu][0] != 0:
                former_file = curr_path + "/" + str(sl[nu][0]) + "/sample.xyz_" + str(sl[nu][1])
                later_file = all_path + "/all_sample.xyz_" + str(nu+1)
                command = "cp " + former_file + " " + later_file
                os.system(command)
    def copy_ci(self):
        
        curr_path = os.getcwd()
        ci_path = curr_path + '/ci'
        all_path = curr_path + "/all"
        os.chdir(ci_path)
        command = 'cp hop_all.xyz input.xyz'
        os.system(command)
        split.make()
        for i in range(self.n_ci):
            command = 'cp all_sample.xyz_' + str(i+1) + ' ' + all_path + '/all_sample.xyz_' + str(self.num+1)
            os.system(command)
            self.savelist[self.num][0] = -1
            self.savelist[self.num][1] = int(i+1)
            self.savelist[self.num][2] = int(self.num+1)
            self.num = self.num +1
        os.chdir(curr_path) 
        print "The select geom in the ci file is %i" % self.n_ci
        return

    def make(self):
        curr_path = os.getcwd()
        all_path = curr_path + "/all"
        if os.path.exists(all_path):
            os.system('rm -r ./all')
        os.makedirs(all_path)

        if self.n_s0 > 0:
            self.copy_s0()

        self.select_coord_many()
        self.copy()

        if self.n_ci > 0:
            self.copy_ci()

#       """Save the list to a file named list_file.dat"""
        list_file = self.list_file
        num = self.num
        sl = self.savelist 
        curr_path = os.getcwd()
        all_path = curr_path + "/all"
        workfile = all_path + "/" + list_file
        fp = open(workfile,"w")
        for i in range(num):
            print >> fp,  "%10d%10d%10d" % (sl[i][0], sl[i][1],sl[i][2])
        fp.close()
        print "The total geom selected is %10d" % self.num
        self.inp['n_geom'] = self.num
        json.dump_json('inp.json',self.inp)
        print "The select work is done"                  
            
if __name__ == "__main__":

    jobs = select_coord()
    jobs.make()    

