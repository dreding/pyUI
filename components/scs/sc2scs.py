
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2010 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""


'''
Created on xx.xx.2012

@author: Dred
'''

"""sc -> scs translator component
"""

from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
'''import scg_alphabet
import scg_objects'''
import suit.core.exceptions as exceptions

session = core.Kernel.session()

def getConstStr(_type):
    _const = None
    sc.SC
    if _type & sc.SC_VAR:
        _const = "var"
    elif _type & sc.SC_A_METAVAR:
        _const = "meta"
    else:
        _const = "-"
    return _const

def getPosStr(_type):
    _pos = None
    if _type & sc.SC_POS:
        _pos = "pos"
    elif _type & sc.SC_NEG:
        _pos = "neg"
    elif _type & sc.SC_FUZ:
        _pos = "fuz"
    else:
        _pos = "-"
    return _pos

def translate_obj(_session, _el, _type):
    """Translates sc-element to object

    @param _session:    current workable session
    @type _session:    sc_session
    @param _el:    sc-element to translate into object
    @type _el:    sc_global_addr
    @param _type:    sc-element type (gets for growing speed)
    @type _type:    sc_type
    @return: created object that represent sc-element
    @rtype: ObjectDepth
    """
    if _type & sc.SC_NODE:
        return translate_node(_session, _el, _type)
    elif _type & sc.SC_ARC:
        return translate_pair(_session, _el, _type)

    return translate_node(_session, _el, _type|sc.SC_NODE)
    #raise RuntimeError("Unknown element type")

def translate_node(_session, _el, _type):
    """Translate sc-node into SCs
    """

    #Check have node content or not
    _cnt_type = sc_utils.getContentFormat(_session, _el)

    if _cnt_type is not None:
        #I don't find any info about view content of nodes in scs
        pass
    else:
        _const = getConstStr(_type)
        if _const == "var":
            return "$_%s" % (sc_utils.getLocalizedIdentifier(_session,_el))
        elif _const == "meta":
            return "$__%s" % (sc_utils.getLocalizedIdentifier(_session,_el))
        return "$%s" % (sc_utils.getLocalizedIdentifier(_session,_el))
    #obj =



def translate_pair(_session, _el, _type):
    """Translate sc-pair into SCs
    """
    type_name = "pair/-/-/-/-"

    _const = getConstStr(_type)
    _pos = getPosStr(_type)
    _orient = "orient"

    assert _pos is not None and _const is not None

    if _type & sc.SC_TEMPORARY:
        type_name = "pair/%s/time/%s/%s" % (_pos, _orient, _const)
    else:
        type_name = "pair/%s/-/%s/%s" % (_pos, _orient, _const)

    #obj = scg_alphabet.createSCgPair(type_name)
    #obj._setScAddr(_el)
    #return obj
    return "$%s" % (sc_utils.getLocalizedIdentifier(_session,_el))

class TranslatorSc2Scs(Translator):
    '''Class for translating from SC into SCS'''
    def __init__(self):
        Translator.__init__(self)

    def __del__(self):
        Translator.__del__(self)

    def translate_impl(self, _input, _output):
        """Translator implementation
        @param _input:    input data set
        @type _input:    sc_global_addr
        @param _output:    output window (must be created)
        @type _output:    sc_global_addr

        @return: list of errors each element of list is a tuple(object, error)
        @rtype: list
        """
        segment = core.Kernel.segment()
        session = core.Kernel.session()
        _segs = [segment.get_full_uri()]
        search_segments =  ["/ui/core",
                            "/seb/belarus",
                            "/seb/planimetry",
                            "/seb/graph",
                            "/seb/rus",
                            "/etc/questions",
                            "/etc/com_keynodes",
                            "/seb/test",
                            "/proc/agents/nsm/keynode"]
        _segs.extend(search_segments)


        el = sc_utils.getElementByIdtf("test2_scs_sc", _segs)
        if el==None:
            return

        errors = []
        objs = objects.ScObject._sc2Objects(_output)

        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet

        session = core.Kernel.session()

        trans_objs = []
        result_objs = []

        # creating list of element to translate
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE), True)
        list_of_addrs = []
        while not it.is_over():
            trans_objs.append(it.value(2))
            list_of_addrs.append(str(it.value(2).this))
            it.next()

        # getting objects on sheet
        childs = sheet.getChilds()
        sc_scs = {}
        object_types = {}
        for obj in childs:
            addr = obj._getScAddr()
            if addr is not None:
                s_addr = str(addr.this)
                sc_scs[s_addr] = obj
                object_types[s_addr] = session.get_type(addr)
                list_of_addrs.append(s_addr)

        ignore_list = []
        process_pairs = []

        # translating binary and noorient pairs and store types
        for obj in trans_objs:
            _type = session.get_type(obj)
            object_types[str(obj.this)] = _type

            if str(obj.this) in ignore_list:
                continue


        #something miss

        # translating objects
        for obj in trans_objs:
            if sc_scs.has_key(str(obj.this)) or (str(obj.this) in ignore_list):
                continue

            _type = object_types[str(obj.this)]

            # checking pairs
            if _type & sc.SC_ARC:
                beg = session.get_beg(obj)
                end = session.get_end(obj)
                if (beg is not None) and (end is not None):
                    if (str(beg.this) in list_of_addrs) and (str(end.this) in list_of_addrs):
                        process_pairs.append((obj, beg, end))
                    else:
                        continue    # skipping dead (haven't begin or end element) pairs


            # translating sc-element to scg-object
            scs_obj = translate_obj(session, obj, object_types[str(obj.this)])

            sc_scs[str(obj.this)] = scs_obj
            # translating identificators
            #            idtf = session.get_idtf(obj)
            #            if not sc_utils.isSystemId(idtf):
            #                scg_obj.setText(idtf)

            #scg_obj.setWasInMemory(True)

            # adding to window
            #sheet.addChild(scg_obj)
            result_objs.append(scs_obj)

