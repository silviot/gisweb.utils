from Products.CMFPlomino.PlominoForm import PlominoForm
from Products.CMFPlomino.PlominoDocument import PlominoDocument
from Products.CMFPlomino.index import PlominoIndex

# Security import
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlomino.config import READ_PERMISSION

PlominoIndex.security = ClassSecurityInfo()
PlominoIndex.security.declareProtected(READ_PERMISSION, 'create_child')
PlominoIndex.security.declareProtected(READ_PERMISSION, 'oncreate_child')
PlominoIndex.security.declareProtected(READ_PERMISSION, 'onsave_child')
PlominoIndex.security.declareProtected(READ_PERMISSION, 'ondelete_child')
PlominoIndex.security.declareProtected(READ_PERMISSION, 'ondelete_parent')
InitializeClass(PlominoDocument)

defaults = dict(
    parentKey = 'parentDocument',
    parentLinkKey = 'linkToParent',
    childrenListKey = 'listOf_%s'
)


def getPath(doc, virtual=False):

    doc_path = doc.doc_path()
    
    pd_path_list = doc.REQUEST.physicalPathToVirtualPath(doc_path) if virtual else None

    return '/'.join(pd_path_list or doc_path)


def setParenthood(ChildDocument, parent_id, CASCADE=True, setDocLink=False, **kwargs):
    '''
    Set parent reference in child document
    '''

    parentKey = kwarg.get('parentKey')s or defaults.get('parentKey')
    parentLinkKey = kwarg.get('parentLinkKey')s or defaults.get('parentLinkKey')
    
    ParentDocument = self.getParentDatabase().getDocument(parent_id)
    Parent_path = getPath(parentDocument)

    ChildDocument.setItem(parentKey, ParentDocument.getId())
    ChildDocument.setItem('CASCADE', CASCADE)
    if setDocLink:
        ChildDocument.setItem(parentLinkKey, [Parent_path])


def setChildhood(ChildDocument, parent_id, backToParent='anchor', **kwargs):
    '''
    Set child reference on parent document
    '''
    
    parentKey = kwarg.get('parentKey')s or defaults.get('parentKey')
    childrenListKey = kwarg.get('childrenListKey')s or defaults.get('childrenListKey')
    
    db = ChildDocument.getParentDatabase()
    ParentDocument = db.getDocument(parent_id)
    
    childrenList_name = childrenListKey % ChildDocument.Form
    childrenList = ParentDocument.getItem(childrenList_name, []) or []
    childrenList.append(getPath(ChildDocument))
    
    idx = db.getIndex()
    for fieldname in (parentKey, 'CASCADE', ):
        if fieldname not in idx.indexes():
            idx.createFieldIndex(fieldname, 'TEXT', refresh=True)
    
    ParentDocument.setItem(childrenList_name, childrenList)
    
    if backToParent:
        backUrl = ParentDocument.absolute_url()
        if backToParent == 'anchor':
            backUrl = '%s#%s' % (backUrl, childrenList_name)
        ChildDocument.setItem('plominoredirecturl', backUrl)


def oncreate_child(self, parent_id='', backToParent='anchor', **kwargs):
    '''
    Actions to perform on creation of a ChildDocument
    '''

    parentKey = kwarg.get('parentKey')s or defaults.get('parentKey')
    
    # if no parent_id passed
    # first take from the child itself
    if not parent_id:
        parent_id = self.getItem(parentKey)
    
    # second take from the request
    if not parent_id:
        parent_id = self.REQUEST.get(parentKey)

    if parent_id:
        setParenthood(self, parent_id, child.id, **kwargs)
        setChildhood(self, parent_id, child.id, backToParent, **kwargs)


def onsave_child(self):
    '''
    Actions to perform on save of a ChildDocument
    '''
    if not self.isNewDocument():
        if self.getItem('plominoredirecturl'):
            self.removeItem('plominoredirecturl')


def ondelete_child(self, anchor=True, **kwargs):
    '''
    Actions to perform on deletion of a ChildDocument
    '''
    
    parentKey = kwarg.get('parentKey')s or defaults.get('parentKey')
    childrenListKey = kwarg.get('childrenListKey')s or defaults.get('childrenListKey')
    
    db = self.getParentDatabase()
    ParentDocument = db.getDocument(self.getItem(parentKey))
    childrenList_name = childrenListKey % self.Form
    childrenList = ParentDocument.getItem(childrenList_name)
    url = getPath(self)
    childrenList.remove(url)
    ParentDocument.setItem(childrenList_name, childrenList)
    
    backUrl = parent.absolute_url()
    if anchor:
        backUrl = '%s#%s' % (backUrl, childrenList_name)
    self.REQUEST.set('returnurl', backUrl)

def ondelete_parent(self, **kwargs):
    '''
    Actions to perform on deletion of a parentDocument
    '''
    
    parentKey = kwarg.get('parentKey')s or defaults.get('parentKey')

    db = self.getParentDatabase()
    idx = db.getIndex()
    request = {parentKey: parent.id}
    res = idx.dbsearch(request)
    toRemove = []
    for rec in res:
        if rec.CASCADE:
            toRemove += [rec.id]
        else:
            rec.getObject().removeItem(parentKey)
    db.deleteDocuments(ids=toRemove, massive=False)


def create_child(self, form_name, request={}, applyhidewhen=True, **kwargs):
    '''
    Use it to create a child document from scripts
    '''

    db = self.getParentDatabase()
    form = db.getForm(form_name)
    ChildDocument = db.createDocument()
    ChildDocument.setItem('Form', form_name)
    form.readInputs(ChildDocument, request, applyhidewhen=applyhidewhen)
    setParenthood(self, parent.id, doc.id, **kwargs)
    setChildhood(self, parent.id, doc.id, **kwargs)
    ChildDocument.save()
    return ChildDocument.getId()


PlominoDocument.create_child = create_child
PlominoDocument.oncreate_child = oncreate_child
PlominoDocument.onsave_child = onsave_child
PlominoDocument.ondelete_child = ondelete_child
PlominoDocument.ondelete_parent = ondelete_parent
