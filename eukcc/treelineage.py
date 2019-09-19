#!/usr/bin/env python
import operator
from ete3 import Tree
from ete3 import NCBITaxa
ncbi = NCBITaxa()


class treeHandler():
    def __init__(self, tree = None, root = False, annotate = True):
        self.loadTree(tree)
        if root:
            self.root()
        if annotate:
            self.annotateTree()
        
    def loadTree(self, tree):
        try:
            self.t = Tree(tree)
        except:
            self.t = Tree(tree, format = 1)
        
    def annotateTree(self):
        i = 0
        for node in self.t.get_tree_root().traverse():
            if node.name == "":
                node.name = "node{}".format(i)
                i += 1
    
    def get_lineage(self, leave, istaxid = True):
        try:
            if istaxid:
                n = self.t.search_nodes(taxid=int(leave))[0]
            else:
                n = self.t.search_nodes(name=leave)[0]
        except:
            print("Node {} not found".format(leave))
            return(False)
        l = []
        while True:
            try:
                l.append(n.name)
                n = n.up
            except:
                break
        l.reverse()
        return(l)
    
    def addTaxids(self, GCAs, taxids):
        for GCA, tax in zip(GCAs, taxids):
            try:
                n = self.t.search_nodes(name=GCA)[0]
                n.add_feature("taxid", int(tax))
            except:
                continue
        
    def root(self):
        # midpoitn rooting
        R = self.t.get_midpoint_outgroup()
        # and set it as tree outgroup
        self.t.set_outgroup(R)
    
    def leaves(self):
        return(self.t.get_tree_root().get_leaf_names())
    
    def children(self, nodename ):
        '''
        find and rturn all leafs belpongin as chidlren
        to a node
        '''
        nn = self.t.search_nodes(name=nodename)[0].get_leaf_names()
        return(nn)

        
    def write(self, file):
        self.t.write(format=1, outfile=file)
    
    def getPlacement(self, mode, sets, nonplacements, nplacements = 2, atleast = 1, debug = False):
        """
        function to find the set that has the most support given either LCA (default)
        or HPA placement .
        returns list of dict
        """
        # get all placements by subtsracting known leaves from all leave names
        placements = set(self.t.get_tree_root().get_leaf_names()) - set(nonplacements)
        remaining = placements
        results = []
        # while we have placements to cover, search for sets
        while nplacements > 0:
            for i in range(len(sets)):
                covering = set(self.children(sets[i]['node'])) & remaining
                sets[i]['cover'] = len(covering)
                sets[i]['covering'] = covering
                sets[i]['nPlacements'] = len(placements)
            
            # get the one with the best coverage sorted by what we need now
            # so we need to sort the list of dicts with different keys
            if mode == "HPA":
                #sets.sort(key=operator.itemgetter("n"), reverse=True)
                sets.sort(key=operator.itemgetter("ngenomes"), reverse=True)
            elif mode == "LCA":
                #sets.sort(key=operator.itemgetter("n"), reverse=True)
                sets.sort(key=operator.itemgetter("ngenomes"), reverse=False)
            else:
                # we dont know what to do
                print("Mode not know", mode)
                return()
            # sort now by cover, keeping the underlying order of genomes in case 
            # several sets cover the same amount of profiles
            sets.sort(key=operator.itemgetter("cover"), reverse=True)
            #for s in sets:
            #    print(s)
           
            # only retain if at least N placements
            i = 0
            if debug:
                maximum = 9999
            else:
                maximum = 1
            # in debug mode we want to return all best placements, not just the LCA or HPA
            while i < maximum and sets[i]['cover'] >= atleast:
                # break if new set has less more than 1 less covers than the best
                if i > 0 and (results[0]['cover'] - sets[i]['cover']) > 1:
                    break
                
                # save set as a result
                results.append(sets[i].copy())
                # add neighbours 
                sisters = []
                # last result item we track which placmeent where covered
                for place in results[-1]['covering']:
                    # we search the sisters of the placement loaction
                    si = self.t.search_nodes(name=place)[0].get_sisters()
                    for sis in si:
                        # and fetch the names of all leaves
                        sisters.extend(sis.get_leaf_names())
                # reducing this to only keep GCA numbers and not pplacer leaves 
                sisters = set(sisters) - placements
                # save in list
                results[-1]['sisters'] = sisters
                # remove remaining
                remaining = remaining - sets[i]['covering']

                # count up i, usually
                i = i + 1
                if debug:
                    print(results[-1])
            
            nplacements -= 1

            
        return(results)
    
    
    
        
    