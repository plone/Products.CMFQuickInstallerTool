from Acquisition import aq_base, aq_inner, aq_parent



def updatelist(a, b, c=None):
    for l in b:
        if not l in a:
            if c is None:
                a.append(l)
            else:
                if not l in c:
                    a.append(l)

def delObjects(cont, ids):
    """ abbreviation to delete objects """
    delids=[id for id in ids if hasattr(aq_base(cont),id)]
    for delid in delids:
        try:
            cont.manage_delObjects(delid)
        except (AttributeError, KeyError, BadRequest):
            LOG("Quick Installer Tool: ", PROBLEM, "Failed to delete '%s' in '%s'" % (delid, cont.id))
