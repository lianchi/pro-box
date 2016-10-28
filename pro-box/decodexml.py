from xml.dom import minidom , Node

class bookscanner:
    def __init__(self,doc):
        for child in doc.childNodes :
            if child.nodeType == Node.ELEMENT_NODE \
            and child.tagName == "book" :
                bookid = child.getAttribute("id")
                print "*"*20
                print "Book id : " , bookid
                self.handle_book(child)

    def handle_book(self,node):
        for child in node.childNodes :
            if child.nodeType == Node.ELEMENT_NODE :
                if child.tagName == "title":
                    print "Title : " , self.getText(child.firstChild)
                if child.tagName == "author":
                    self.handle_author(child)
                if child.tagName == "pubdate":
                    print "Pubdate : " , self.getText(child.firstChild)

    def getText(self,node):
        if node.nodeType == Node.TEXT_NODE :
            return node.nodeValue
        else: return ""

    def handle_author(self,node):
        author = node.firstChild
        for child in author.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.tagName == "firstname" :
                    print "Firstname : ", self.getText(child.firstChild)
                if child.tagName == "lastname" :
                    print "Lastname : " , self.getText(child.firstChild)


doc = minidom.parse("device.xml")
root = doc.getElementsByTagName('root')
print root.length

for child in doc.childNodes :
    print child
    print child.nodeType,child.nodeValue
    if child.nodeType == Node.COMMENT_NODE:
        print "Conment : " , child.nodeValue
    if child.nodeType == Node.ELEMENT_NODE:
        bookscanner(child)