# $Id$
#
#  Copyright (C) 2003-2006  greg Landrum and Rational Discovery LLC
#
#   @@ All Rights Reserved  @@
#
import RDConfig
import DbModule
import sys
sqlTextTypes = DbModule.sqlTextTypes
sqlIntTypes = DbModule.sqlIntTypes
sqlFloatTypes = DbModule.sqlFloatTypes
sqlBinTypes = DbModule.sqlBinTypes


def GetDbNames(user='sysdba',password='masterkey',dirName='.',dBase='::template1'):
  """ returns a list of databases that are available

    **Arguments**

      - user: the username for DB access

      - password: the password to be used for DB access

    **Returns**

      - a list of db names (strings)

  """
  if DbModule.getDbSql:
    try:
      cn = DbModule.connect(dBase,user,password)
    except:
      print 'Problems opening database: %s'%(dBase)
      return []
    c = cn.cursor()
    c.execute(DbModule.getDbSql)
    if RDConfig.usePgSQL:
      names = ['::'+str(x[0]) for x in c.fetchall()]
    else:
      names = ['::'+str(x[0]) for x in c.fetchall()]
    names.remove(dBase)
  elif DbModule.fileWildcard:
    import os.path,glob
    names = glob.glob(os.path.join(dirName,DbModule.fileWildcard))
  else:
    names = []
  return names


def GetTableNames(dBase,user='sysdba',password='masterkey',
                  includeViews=0):
  """ returns a list of tables available in a database

    **Arguments**

      - dBase: the name of the DB file to be used

      - user: the username for DB access

      - password: the password to be used for DB access

      - includeViews: if this is non-null, the views in the db will
        also be returned

    **Returns**

      - a list of table names (strings)

  """
  try:
    cn = DbModule.connect(dBase,user,password)
  except:
    print 'Problems opening database: %s'%(dBase)
    return []
  c = cn.cursor()
  if not includeViews:
    comm = DbModule.getTablesSql
  else:
    comm = DbModule.getTablesAndViewsSql
  c.execute(comm)
  names = [str(x[0]).upper() for x in c.fetchall()]
  if RDConfig.usePgSQL and 'PG_LOGDIR_LS' in names:
    names.remove('PG_LOGDIR_LS')
  return names



def GetColumnInfoFromCursor(cursor):
  if cursor is None or cursor.description is None: return []
  results = []
  for item in cursor.description:
    cName = item[0]
    cType = item[1]
    if cType in sqlTextTypes:
      typeStr='string'
    elif cType in sqlIntTypes:
      typeStr='integer'      
    elif cType in sqlFloatTypes:
      typeStr='float'
    elif cType in sqlBinTypes:
      typeStr='binary'
    else:
      sys.stderr.write('odd type in col %s: %s\n'%(cName,str(cType)))
    results.append((cName,typeStr))
  return results
  
def GetColumnNamesAndTypes(dBase,table,
                           user='sysdba',password='masterkey',
                           join='',what='*'):
  """ gets a list of columns available in a DB table along with their types

    **Arguments**

      - dBase: the name of the DB file to be used

      - table: the name of the table to query

      - user: the username for DB access

      - password: the password to be used for DB access

      - join: an optional join clause (omit the verb 'join')

      - what: an optional clause indicating what to select

    **Returns**

      - a list of 2-tuples containing:

          1) column name

          2) column type

  """
  cn = DbModule.connect(dBase,user,password)
  c = cn.cursor()
  cmd = 'select %s from %s'%(what,table)
  if join:
    cmd += ' join %s'%(join)
  c.execute(cmd)
  return GetColumnInfoFromCursor(c)

def GetColumnNames(dBase,table,user='sysdba',password='masterkey',
                   join='',what='*'):
  """ gets a list of columns available in a DB table

    **Arguments**

      - dBase: the name of the DB file to be used

      - table: the name of the table to query

      - user: the username for DB access

      - password: the password to be used for DB access

      - join: an optional join clause  (omit the verb 'join')

      - what: an optional clause indicating what to select

    **Returns**

      -  a list of column names

  """
  cn = DbModule.connect(dBase,user,password)
  c = cn.cursor()
  cmd = 'select %s from %s'%(what,table)
  if join:
    if join.strip().find('join') != 0:
      join = 'join %s'%(join)
    cmd +=' ' + join
  c.execute(cmd)
  c.fetchone()
  desc = c.description
  res = map(lambda x:str(x[0]),desc)
  return res
