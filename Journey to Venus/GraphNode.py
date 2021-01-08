# Jittipat Shobbakbun
# 11/05/2020
# GraphNode.py

class Node:
    '''GraphNode Object, has data and links'''
    def __init__(self,data,*args):
        '''Creats a GraphNode object with data'''
        self.data = data
        self.links = []
        for node in args:
            if node not in self.links:
                self.links.append(node)

    def getData(self):
        '''Gets the data'''
        return self.data

    def setData(self,data):
        '''Sets the data'''
        self.data = data

    def getLinks(self):
        '''Gets the links'''
        return self.links

    def setLinks(self,links):
        '''Sets the links'''
        self.links = links

    def __repr__(self):
        '''Returns a string representation of the node'''
        return str(self.data)

    def link(self,other):
        '''Links one node to the other in both directions'''
        self.links.append(other)
        other.links.append(self)

    def checkLink(self,other):
        '''Checks if two nodes are linked'''
        if other in self.links and self in other.links:
            return True
        else:
            return False

def main():
    '''Test code for GraphNode'''
    ME = Node("Maine")
    VT = Node("Vermont")
    NH = Node("New Hampshire")
    MA = Node("Massachusetts")
    CT = Node("Connecticut")
    RI = Node("Rhode Island")

    ME.link(NH)
    VT.setLinks([NH,MA])
    NH.setLinks([VT,ME,MA])
    MA.setLinks([VT,NH,CT,RI])
    CT.setLinks([MA,RI])
    RI.setLinks([MA,CT])

    print(NH.checkLink(MA))
    print(NH.checkLink(CT))
    print(NH.getLinks())

if __name__ == "__main__":
    main()
