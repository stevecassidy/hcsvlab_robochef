# -*- coding: utf-8 -*-
from pyparsing import *
import re

def parseResultsCmp(pr1, pr2):
  """
  Compare two pyparsing ParseResults.  Necessary because pyparsing does not
  define equality on this type.
  >>> parseResultsCmp(ParseResults([],{}), ParseResults([],{}))
  0
  >>> parseResultsCmp(ParseResults([1,2,3], {}), ParseResults([], {}))
  1
  >>> parseResultsCmp(ParseResults([1,2,3], {}), ParseResults([1,2,3], {}))
  0
  """
  if (cmp(pr1.asList(), pr2.asList()) == 0):
    return cmp(pr1.asDict(), pr2.asDict())
  else:
    return cmp(pr1.asList(), pr2.asList())

def replaceEntitiesInStr(text):
  # + is inserted for in-word line breaks, remove it
  text = re.sub(r'\+', '', text)
  # Fix lonely ampersands
  text = re.sub(r'(\s)\&(\s)', r'\1&amp;\2', text)
  # Fix &c (etc)
  text = text.replace('&c.', '&amp;c.')
  # Fix <= and >=
  text = text.replace('<=', '&lt;=')
  text = text.replace('>=', '&gt;=')
  text = re.sub(r'<(\s*)(\d)', r'&lt;\1\2', text)
  text = re.sub(r'(\s+)>(\s*)(\d)', r'\1&gt;\2\3', text)

  # Replace non-XML entities
  text = text.replace('&pound;', u'\u00a3')
  text = text.replace('&pounds;', u'\u00a3')
  text = text.replace('&reg;', u'\u00ae')
  text = text.replace('&degree;', u'\u00b0')
  text = text.replace('&degrees;', u'\u00b0')
  text = text.replace('&deg;', u'\u00b0')
  text = text.replace('&para;', u'\u00b6')
  text = text.replace('&bullet;', u'\2022')
  text = text.replace('&sup;', u'\u2283')

  text = text.replace('&Alpha;', u'\u0391')
  text = text.replace('&Beta;', u'\u0392')
  text = text.replace('&Gamma;', u'\u0393')
  text = text.replace('&Delta;', u'\u0394')
  text = text.replace('&Epsilon;', u'\u0395')
  text = text.replace('&Zeta;', u'\u0396')
  text = text.replace('&Eta;', u'\u0397')
  text = text.replace('&Rheta;', u'\u0398')
  text = text.replace('&Iota;', u'\u0399')
  text = text.replace('&Kappa;', u'\u039a')
  text = text.replace('&Lambda;', u'\u039b')
  text = text.replace('&Mu;', u'\u039c')
  text = text.replace('&Nu;', u'\u039d')
  text = text.replace('&Xi;', u'\u039e')
  text = text.replace('&Omicron;', u'\u039f')
  text = text.replace('&Pi;', u'\u03a0')
  text = text.replace('&Rho;', u'\u03a1')
  text = text.replace('&Sigmaf;', u'\u03a2')
  text = text.replace('&Sigma;', u'\u03a3')
  text = text.replace('&Tau;', u'\u03a4')
  text = text.replace('&Upsilon;', u'\u03a5')
  text = text.replace('&Phi;', u'\u03a6')
  text = text.replace('&Chi;', u'\u03a7')
  text = text.replace('&Psi;', u'\u03a8')
  text = text.replace('&Omega;', u'\u03a9')

  text = text.replace('&alpha;', u'\u03b1')
  text = text.replace('&beta;', u'\u03b2')
  text = text.replace('&gamma;', u'\u03b3')
  text = text.replace('&delta;', u'\u03b4')
  text = text.replace('&epsilon;', u'\u03b5')
  text = text.replace('&zeta;', u'\u03b6')
  text = text.replace('&eta;', u'\u03b7')
  text = text.replace('&theta;', u'\u03b8')
  text = text.replace('&iota;', u'\u03b9')
  text = text.replace('&kappa;', u'\u03ba')
  text = text.replace('&lambda;', u'\u03bb')
  text = text.replace('&mu;', u'\u03bc')
  text = text.replace('&nu;', u'\u03bd')
  text = text.replace('&xi;', u'\u03be')
  text = text.replace('&omicron;', u'\u03bf')
  text = text.replace('&pi;', u'\u03c0')
  text = text.replace('&rho;', u'\u03c1')
  text = text.replace('&sigmaf;', u'\u03c2')
  text = text.replace('&sigma;', u'\u03c3')
  text = text.replace('&tau;', u'\u03c4')
  text = text.replace('&upsilon;', u'\u03c5')
  text = text.replace('&phi;', u'\u03c6')
  text = text.replace('&chi;', u'\u03c7')
  text = text.replace('&psi;', u'\u03c8')
  text = text.replace('&omega;', u'\u03c9')

  text = text.replace('&formula;', '?')
  text = text.replace('&symbol;', '?')
  text = text.replace('&SYMBOL;', '?')
  
  return text

def putLTBack(text):
  text = text.replace('&lt;', '<')
  return text
  
## parsing tables
def tableParser(cols):
  """
  This function will parse a table in the format that antiword gives us from the Monash Word files.  Tables are
  pipe delimited and there are no row markers.  We assume each new line is a row in this function and arrayToMeta
  takes care of working out when this was not the right assumption
  """
  delim = Suppress(Literal(u"|"))
  cellData = CharsNotIn(u"|\n").leaveWhitespace().setParseAction(lambda x: x[0].strip())
  rowParser = delim
  for i in range(0,cols):
    rowParser = rowParser + cellData + delim
  return OneOrMore(rowParser).setParseAction(lambda x, loc, toks: arrayToMeta(fillArray(toks,cols)))

def fillArray(onedarr, cols):
  """
  Converts a one dimensional array into a two dimensional array based on the number
  of colums given
  """
  twodarr = []
  for i in range(0, len(onedarr)/cols):
    twodarr.append(onedarr[i*cols:(i+1)*cols])
  return twodarr

def arrayToMeta(data):
  """
  Takes a two dimensional array of strings and converts them to
  key value pairs according to the following rules:
    * the outer/first dimension is columns
    * odd numbered colums are keys, even numbered columns are values
    * a key or a value can span two lines/rows in which case it should
      be appended to the row above.
    * no such value should ever be in the first column, so a blank element in
      the first column is an indicator that the values in this column should
      be appended to those above it.  "INITIALS:" is an exception to this rule
  >>> arrayToMeta([['a','aval', 'b', 'bval']])
  {'a': 'aval', 'b': 'bval'}
  >>> arrayToMeta([['a','aval', 'b', 'bval'], ['', 'more a', '', 'more b'], ['c', 'cval', 'd', 'dval'], ['', '', 'd is complicated', 'as is its val']])
  {'a': 'aval more a', 'c': 'cval', 'b': 'bval more b', 'd d is complicated': 'dval as is its val'}
  """
  def arrConcat(a1, a2):
    res = a1
    splitter = ''
    for i in range(0, len(a1)):
      if a2[i] != "": splitter = " " 
      else:           splitter = ""
      res[i] = res[i] + splitter +  a2[i]
    return res

  # flatten cells that are over two rows
  flatData = []
  lastGoodRow = 0
  for ri, row in enumerate(data):
    if ((data[ri][0] == "") | (data[ri][0]=="INITIALS:")):
      extraRow = True
    else:
      extraRow    = False

    if (not extraRow):
      flatData.append(data[ri])
      lastGoodRow = len(flatData) - 1
    else:
      flatData[lastGoodRow] = arrConcat(flatData[lastGoodRow], data[ri])

  # go through the flattened data and create a dictionary
  res = {}
  for row in flatData:
    for ci in range(0, len(row), 2):
      res[row[ci]] = row[ci+1]

  return res


def toXMLName(ustr):
    """
    convert given unicode string to a valid XML Name.
    see http://www.w3.org/TR/REC-xml/#NT-CombiningChar

    The resulting string is constructed by removing all illegal characters from the input string.

    >>> toXMLName(u'This will be reduced to (x)')
    u'Thiswillbereducedtox'
    >>> toXMLName('Only Unicode as input')
    Traceback (most recent call last):
      ...
    TypeError: must be unicode, not str

    There must be something left at the end.
    >>> toXMLName(u'&&((-))')
    Traceback (most recent call last):
      ...
    Exception: can't convert &&((-)) to xmlname
    >>> toXMLName(u'&&((_-))')
    u'_-'
    """
    from unicodedata import category, decomposition
    NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
    NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
    ALLOWED_NAME_START_CHARS = [u"_"] # u":" can't be part of NCNames
    ALLOWED_NAME_CHARS = ALLOWED_NAME_START_CHARS + [u"\u00B7", u"\u0387", u"-", u"."]

    ret = []
    start = True
    for c in ustr:
        if start:
            if not category(c) in NAME_START_CATEGORIES and c not in ALLOWED_NAME_START_CHARS:
                continue
            start = False
        else:
            if not category(c) in NAME_CATEGORIES and c not in ALLOWED_NAME_CHARS:
                continue
        ret.append(c)
    if not ret:
        raise Exception("can't convert %s to xmlname" % ustr)
    return ''.join(ret)


def add_to_dictionary(key, dict1, dict2):
    '''
    This method adds a dictionary to an existing dictionary. Overlapping keys in the second dictionary are prioritised over those
    in the first dictionary
     '''
    if key in dict1:
      if type(dict1[key]) == type({}):
        dict1[key] = merge_dictionaries(dict1[key], dict2)
        return dict1
      else:
        return merge_dictionaries(dict1, dict2)
    else:
      dict1[key] = dict2
      return dict1
      

def merge_dictionaries(dict1, dict2):
    '''
    This method merges two dictionaries, if the two dictionaries contain similar keys, it picks the key with the non empty
    value, simply updating dictionaries using the update method is insufficient
    '''
    new_dict = {}

    for key, value in dict1.iteritems():

      # If the key does not exist in the second dictionary then just add this one to the new dictionary
      # If there is a value pick the non empty one and delete the key from the old
      if (dict2.get(key) == None) or (dict2.get(key) == ""):
        new_dict[key] = value
      else:
          new_dict[key] = dict2[key]

      # After this is done delete the item from the second dictionary
      if dict2.get(key) != None:
        del dict2[key]

    # After all this is done just merge the remaining items
    new_dict.update(dict2)  
    return new_dict