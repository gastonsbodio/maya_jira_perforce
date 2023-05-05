from __future__ import division
from functools import partial
import traceback
import ast
import sys
import os
import time
from threading import Thread


import pydrive
from pydrive import auth
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class googleDrToPrg():
#
	def login(self):
		gauth = GoogleAuth( )
		GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = var_prG + '/PACKAGES/creds/client_secrets.json'

		c = gauth.LoadCredentialsFile(var_prG + "/PACKAGES/creds/mycreds.txt")

		if gauth.credentials is None or c is None:
			gauth.LocalWebserverAuth()
		elif gauth.access_token_expired:
			try:
				gauth.Refresh()
			except Exception:
				gauth.Authorize(c)
		else:
			gauth.Authorize()
		gauth.SaveCredentialsFile(var_prG + "/PACKAGES/creds/mycreds.txt")
		return GoogleDrive(gauth)

	def subir_archivo(self, ruta_archivo, id_folder):
		try:
			drive ='drive#fileLink'
			archivo = self.credenciales.CreateFile({'parents':[{'kind': drive , 'id': id_folder}] })
			archivo['title']= ruta_archivo.split('/')[-1]
			archivo.SetContentFile(ruta_archivo)
			archivo.Upload()
		except Exception as err:
			print (err)
			print ('try warning')

	def dowlo_file(self, googleFi ,ruta_descarga, userIdSlack, projId , signalQth, signalPrint):
		alredyDwLS = []
		nombre_archivo = googleFi['title']
		path = os.path.join( ruta_descarga , nombre_archivo )
		if os.path.isfile( path ):
			tim_local = os.stat(path).st_mtime
			fecha =time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(path)))
			hora = time.ctime(os.path.getmtime(path))
			hora = hora.split(" ")[-2]
			fechaLocalFi = fecha + "T" + hora
			modifArchivo = googleFi['modifiedDate']
			fechaModGoogFi = modifArchivo.split(".")[0]
			fechaModGoogFi = self.timeFixer( fechaModGoogFi, 3)
			if signalPrint:
				print (' . . . . . . . . . .  ')
				print (fechaModGoogFi)
				print ('GoogleD Date')
				print (' ')
				print (fechaLocalFi)
				print ('Local Date')
				print (' . . . . . . . . . .  ')
			if len(googleFi['mimeType'].split('folder')) >1:
				#print ('')
				pass
			else:
				if ruta_descarga+nombre_archivo not in alredyDwLS:
					if fechaModGoogFi > fechaLocalFi:
						if not os.path.exists( ruta_descarga ):
							try:
								os.makedirs(ruta_descarga)
							except Exception:
								pass
						googleFi.GetContentFile( ruta_descarga + nombre_archivo)
						if signalPrint:
							print ('  --  --  --  --  --  --  ')
							mesnajeBot = "    downloading:    " + ruta_descarga + nombre_archivo
							print (mesnajeBot)
						alredyDwLS.append(ruta_descarga + nombre_archivo)
					else:
						if signalPrint:
							print ('  --  --  --  --  --  --  ')
							mesnajeBot = nombre_archivo + "   is already updated"
							print (mesnajeBot)

		else:
			if len(googleFi['mimeType'].split('folder')) <2 :#si es un archivo
				if ruta_descarga+nombre_archivo not in alredyDwLS:
					if not os.path.exists( ruta_descarga ):
						try:
							os.makedirs(ruta_descarga)
						except Exception:
							pass
					googleFi.GetContentFile( ruta_descarga + nombre_archivo)
					if signalPrint:
						print ('  --  --  --  --  --  --  ')
						mesnajeBot = "    downloading:    " + ruta_descarga+nombre_archivo
						print (mesnajeBot)
					alredyDwLS.append(ruta_descarga + nombre_archivo)
			else:
				###decididamente es un folder
				
				####  #  #  ruta_descarga + nombre_archivo
				
				#self.credenciales = self.login()
				gooChilFi=[]
				finalFolderLs=[]
				id = googleFi['id']
				query = " '%%%s%%' in parents and trashed=false"%(id)
				query = query.replace('%','')
				childrenList = self.credenciales.ListFile({'q': query }).GetList()
				if childrenList != []:
					count = len (childrenList)
					key = True
					#while key:
					if True:
						for i , gooD in enumerate(childrenList):
							if len(gooD['mimeType'].split('folder')) >1:

								id = gooD['id']
								query = " '%%%s%%' in parents and trashed=false"%(id)
								query = query.replace('%','')
								childrenLs = self.credenciales.ListFile({'q': query }).GetList()
								if childrenLs != []:
									for idx,gooE in enumerate(childrenLs):

										if len(gooE['mimeType'].split('folder')) <2:
											if gooE not in gooChilFi:
												gooChilFi.append( (gooE, ruta_descarga+gooD['title']+"/") )
										elif len(gooE['mimeType'].split('folder')) >1:
											id = gooE['id']
											query = " '%%%s%%' in parents and trashed=false"%(id)
											query = query.replace('%','')
											childrenLs2 = self.credenciales.ListFile({'q': query }).GetList()
											if childrenLs2 != []:
													
												for idx,gooF in enumerate(childrenLs2):
													if len(gooF['mimeType'].split('folder')) <2:
														if gooF not in gooChilFi:
															gooChilFi.append((gooF, ruta_descarga+gooD['title']+"/"+gooE['title']+"/") )
													elif len(gooF['mimeType'].split('folder')) >1:
														id = gooF['id']
														query = " '%%%s%%' in parents and trashed=false"%(id)
														query = query.replace('%','')
														childrenLs3 = self.credenciales.ListFile({'q': query }).GetList()
														if childrenLs3 != []:

															for idx,gooG in enumerate(childrenLs3):
																if len(gooG['mimeType'].split('folder')) <2:
																	if gooG not in gooChilFi:
																		gooChilFi.append((gooG, ruta_descarga+gooD['title']+"/"+gooE['title']+"/"+gooF['title']+"/"))
																elif len(gooG['mimeType'].split('folder')) >1:
																	id = gooG['id']
																	query = " '%%%s%%' in parents and trashed=false"%(id)
																	query = query.replace('%','')
																	childrenLs4 = self.credenciales.ListFile({'q': query }).GetList()
																	if childrenLs4 != []:


																		for idx,gooH in enumerate(childrenLs4):
																			if len(gooH['mimeType'].split('folder')) <2:
																				if gooH not in gooChilFi:
																					gooChilFi.append((gooH,ruta_descarga+gooD['title']+"/"+gooE['title']+"/"+gooF['title']+"/"+gooG['title']+"/"))
																			elif len(gooH['mimeType'].split('folder')) >1:
																				id = gooH['id']
																				query = " '%%%s%%' in parents and trashed=false"%(id)
																				query = query.replace('%','')
																				childrenLs5 = self.credenciales.ListFile({'q': query }).GetList()
																				if childrenLs5 != []:

																					for idx,gooI in enumerate(childrenLs5):
																						if len(gooI['mimeType'].split('folder')) <2:
																							if gooI not in gooChilFi:
																								gooChilFi.append((gooI,ruta_descarga+gooD['title']+"/"+gooE['title']+"/"+gooF['title']+"/"+gooG['title']+"/"+gooH['title']+"/"))
																						elif len(gooI['mimeType'].split('folder')) >1:
																							id = gooI['id']
																							query = " '%%%s%%' in parents and trashed=false"%(id)
																							query = query.replace('%','')
																							childrenLs6 = self.credenciales.ListFile({'q': query }).GetList()
																							if childrenLs6 != []:
																								for idx,gooJ in enumerate(childrenLs6):
																									if len(gooJ['mimeType'].split('folder')) <2:
																										if gooJ not in gooChilFi:
																											gooChilFi.append((gooJ,ruta_descarga+gooD['title']+"/"+gooE['title']+"/"+gooF['title']+"/"+gooG['title']+"/"+gooH['title']+"/"+gooI['title']+"/"))
																									#elif len(gooJ['mimeType'].split('folder')) >1:
																									#	id = gooJ['id']
																									#	query = " '%%%s%%' in parents and trashed=false"%(id)
																									#	query = query.replace('%','')
																									#	childrenLs7 = self.credenciales.ListFile({'q': query }).GetList()
																										#if childrenLs7 != []:
																							
																							
							else:
								if gooD not in gooChilFi:
									gooChilFi.append( (gooD, ruta_descarga ) )


				for i, gf in enumerate(gooChilFi):
					if gf[0]["id"] not in alredyDwLS:
						if not os.path.exists(gf[1]):
							try:
								os.makedirs(gf[1])
							except Exception:
								pass
						gf[0].GetContentFile( str(gf[1]+gf[0]['title'] ) )
						if signalPrint:
							print ('  --  --  --  --  --  --  ')
							mesnajeBot = "    downloading:    " + gf[1]+gf[0]['title']
							print (mesnajeBot)
							print ('  --  --  --  --  --  --  ')
						alredyDwLS.append( gf[0]["id"] )


	def borrarFi (self, pathLs2Del,projName):
		self.credenciales = self.login()
		for fiPath in pathLs2Del:
			namee = fiPath.split('/')[-1]
			onlyPAth =	self.pathOnlyBuilt( fiPath )
			#onlyPAth = fiPath.split(namee)[0]
			tuplas = self.builtPathSinceRoot ( onlyPAth, projName, self.credenciales)
			if tuplas != False:

				id = tuplas[1].split('/')[-1]

				query = " '%%%s%%' in parents and title = '%%%s%%'"%(id,namee)
				query = query.replace('%','')
				dicFiGD = self.credenciales.ListFile({'q': query}).GetList()
				for obj in dicFiGD:
					obj.Delete()


	def buscar ( self, query):
		resultado =[]
		lista_archivos = self.credenciales.ListFile({'q': query}).GetList()
		for f in lista_archivos:
			resultado.append(f)
		return resultado


	def pathOnlyBuilt (self, pathh):		
		allFolNaLs = pathh.split ("/")
		pathOnly = ''		
		for idx , partFol in enumerate(allFolNaLs):
			if partFol != '':
				resta = 1
				if allFolNaLs[-1] == '':
					resta = 2
				if idx != len(allFolNaLs)-resta:
					pathOnly = pathOnly+partFol+'/'
		return pathOnly

	def builtPathSinceRoot (self, pathh, projRootNa, credenciales):
		projName = projRootNa.split('/')[-1]
		self.credenciales = credenciales
		fileName = pathh.split('/')[-1]
		
		if fileName == '':
			fileName = pathh.split('/')[-2]

		pathOnly = self.pathOnlyBuilt(pathh)
		#allFolNaLs = pathh.split ("/")
		#pathOnly = ''		
		#for idx , partFol in enumerate(allFolNaLs):
		#	if partFol != '':
		#		resta = 1
		#		if allFolNaLs[-1] == '':
		#			resta = 2
		#		if idx != len(allFolNaLs)-resta:
		#			pathOnly = pathOnly+partFol+'/'
			
		pathOnly = pathOnly.split(projName)[-1]
		partsPathNa = pathOnly.split('/')

		keyOneFol = False
		keyProjFol = False
		if pathOnly == '/' :
			keyOneFol = True
			pathOnly = '/'+fileName
			partsPathNa = [fileName]
		else:
			if pathOnly.endswith(':/'):
				keyProjFol = True
				pathOnly = '/'+fileName
				partsPathNa = [fileName]
			else:
				pass
				#print (' ')
		try:
			partsPathNa.remove('')
		except Exception:
			pass
		try:
			partsPathNa.remove('')
		except Exception:
			pass
		cantFolLev = len(partsPathNa)
		dicFileGooD = self.credenciales.ListFile({'q': "title = '%s' and trashed = false and mimeType  contains 'folder'" %projName}).GetList()
		pathInGooglId = ''
		pathInGoogl = ''
		objGooLast = ''
		if dicFileGooD != []:
			for idx, fol in enumerate(partsPathNa):
				if fol != '':
					for gooObj in dicFileGooD: #la primera vez soon los gooObj con nombre Proyecto
						id = gooObj['id']
						if keyProjFol:
							pathInGooglId = '/'+gooObj['id']
							pathInGoogl = '/'+gooObj['title']
							objGooLast = gooObj
							keyLast = True
							break
						else:
							query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%'"%(id,partsPathNa[idx])
							query = query.replace('%','')
							childrenLs_list = self.credenciales.ListFile({'q':query}).GetList()
							if childrenLs_list !=[]:# and cantFolLev-1 > idx + 1:
								key = True
								keyLast = False
								for chil in childrenLs_list:
									if chil['title']==fol:
										for i, f in enumerate(partsPathNa) :
											if fol == f:
												chName = partsPathNa[i]
										dicFileGooD = [chil]
										pathInGooglId = pathInGooglId + gooObj['id'] + '/'
										pathInGoogl = pathInGoogl + gooObj['title'] + '/'
										objGooLast = gooObj
										id = chil['id']
										if keyOneFol == False:
											if cantFolLev-1== idx:
												query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%'"%(id, fileName)
												query = query.replace('%','')
												childrenLs_list = self.credenciales.ListFile({'q': query }).GetList()
												for chil in childrenLs_list:
													if chil['title']==fileName:
														pathInGooglId = pathInGooglId + chil['id']
														pathInGoogl = pathInGoogl + chil['title']
														objGooLast = chil
														keyLast = True
														break
											else:
												query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%'"%(id, chName)
												query = query.replace('%','')
												childrenLs_list = self.credenciales.ListFile({'q': query }).GetList()
										else:
											pathInGooglId = pathInGooglId + chil['id']
											pathInGoogl = pathInGoogl + chil['title']
											objGooLast = chil
											keyLast = True
											break
							else:
								return False
		else:
			return False
		if pathInGoogl.endswith(fileName):
			return ( pathInGoogl, pathInGooglId , objGooLast)
		else:
			return False

	def buildPathGooD( self, dicGoFileList ):
		pathTuple = []
		fatherID = ''
		for idx, f in enumerate(dicGoFileList):
			parented = f['parents'][0]['isRoot']
			pathh = ''
			if len(pathh.split('/')) < 2:
				pathh = f['title']
			if f['parents'][0]['isRoot'] == False:
				fatherID = f['parents'][0]['id']
			allFolders = self.credenciales.ListFile({'q': "mimeType  contains 'folder' and trashed = false"}).GetList()
			name_id_dicc = {}
			while parented == False:
				for fol in allFolders:
					if fol['id'] == fatherID:
						pathh = str ( fol['title'] ) + "/"+ pathh
						if fol['parents'] != []:
							fatherID = fol['parents'][0]['id']
							parented = fol['parents'][0]['isRoot']
						else:
							parented = True
				if idx == len(dicGoFileList) -1 :
					break
			gRoot = ''
			for f in allFolders:
				if fatherID == f['id']:
					gRoot = f['title']
			pathh = gRoot +'/'+ pathh
			pathTuple.append(pathh)
		return pathTuple

	def armarListAllFi(self):
		self.credenciales = self.login()
		dicFileGooD = self.credenciales.ListFile({'q': "mimeType  != 'application/vnd.google-apps.folder'" }).GetList()
		listaPreFinal = self.buildPathGooD( dicFileGooD )
		listaFinal=[]
		for obj in listaPreFinal:
			if obj.startswith('/ADDICTED') or obj.startswith('ADDICTED'):
				listaFinal.append(obj)
		self.slackBot( str(listaFinal), 'U026FCGJ6Q4', 'xoxb-2036648847364-2202460139543-lrWYg5aokVQ7R8h5ZcW9Cmnh' )

	def createPathGooD(self, pathh, projRootName):

		fiName =  pathh.split('/')[-1]
		#dirvePath = pathh.split(fiName)[0]
		dirvePath =	self.pathOnlyBuilt( pathh )
		self.projName = projRootName.split('/')[-1]
		dirvePath = dirvePath.split( projRootName )[-1]
		dirvePath = self.projName + dirvePath
		pathhFolLs = dirvePath.split('/')
		pathhFolLs.remove('')

		dicFileGooD = self.credenciales.ListFile({'q': "title = '%s' and trashed = false" %self.projName}).GetList()

		if [] != dicFileGooD:
			for dr in dicFileGooD:
				if dr['parents'] != []:
					if dr['parents'][0]['isRoot']:
						projectId = dr['id']
				else:
					projectId = dr['id']
		for i, f in enumerate (pathhFolLs):
			if i == 0:
				fatherId = projectId # deberia existir la carpeta del proyecto por eso solo asigno el id para el que venga
			else:

				query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%'"%(fatherId,f)
				query = query.replace('%','')
				dicFileGooD = self.credenciales.ListFile({'q':query}).GetList()

				eximed = []
				if [] != dicFileGooD:
					for dr in dicFileGooD:
						key = True
						try:
							bla = dr['parents'][0]['id']
						except Exception:
							key = False
						if key:
							if fatherId == dr['parents'][0]['id']:
								if f not in eximed:
									eximed.append(f)
								fatherId = dr['id']
								break
						else:
							# aca hay que crear un if para discriminar a las carp
							## ANM o Sequence  o todas aquellas que se repitan muchas veces
							key = False
							for gd in dicFileGooD:
								try:
									if fatherId == gd['parents'][0]['id']:
										key = True
								except Exception as err:
									print ("try warning ")
									print (err)
							if key == False:
								folder = self.credenciales.CreateFile({'title' : f, "parents":  [{"id": fatherId}], 'mimeType' : 'application/vnd.google-apps.folder'})
								folder.Upload()	
								if f not in eximed:
									eximed.append(f)							
								fatherId = folder['id']
								break
				else:
					folder = self.credenciales.CreateFile({'title' : f, "parents":  [{"id": fatherId}], 'mimeType' : 'application/vnd.google-apps.folder'})
					folder.Upload()						
					fatherId = folder['id']
		return fatherId

	def listByNameAndReturn(self, path, projName):
		self.projName = projName
		self.credenciales = self.login()
		listaFinal = []
		if len ( path.split('/') ) > 1:
			fiName = path.split('/')[-1]
			#rootpath = path.split( fiName )[0]
			rootpath = self.pathOnlyBuilt( path )
			
			if rootpath.endswith('/'):
				partes = rootpath.split('/')
				if partes[-1] == '':
					name = partes[-2]
				else:
					name = partes[-1]
				#ruta = rootpath.split(name)[0]
				ruta =	self.pathOnlyBuilt( rootpath )
				onlyPath = ruta + name
			else:
				onlyPath = rootpath
			
			tuplas = self.builtPathSinceRoot ( onlyPath, self.projName, self.credenciales)
			if tuplas != False:
				idFather = tuplas[1].split('/')[-1]
				query = " '%%%s%%' in parents and trashed=false and title contains '%%%s%%' "%(idFather,fiName)
				query = query.replace('%','')
				childrenLs_list = self.credenciales.ListFile({'q':query}).GetList()
				for obj in childrenLs_list:
					listaFinal.append( tuplas[0] + '/' + obj['title'])
		else:
			dicFiGD = self.credenciales.ListFile({'q': "title contains '%s' and trashed = false" %path}).GetList()
			filterList = []
			for gObj in dicFiGD:
				if len (gObj['title'].split(path) ) >1:
					filterList.append( gObj )
			if dicFiGD != []:
				listaPreFinal = self.buildPathGooD( dicFiGD )
				for item in listaPreFinal:
					if len( item.split(projName) ) > 1:
						listaFinal.append(item)
		return listaFinal

	#### Complex functions***********

	def explorePathCloud(self, targetPath, projName , win):
		self.projName = projName
		self.credenciales = self.login()
		tuplas = self.builtPathSinceRoot ( targetPath, self.projName,self.credenciales)
		if tuplas != False:
			id = tuplas[1].split('/')[-1]
			link = 'https://drive.google.com/drive/u/1/folders/%s' %id
			import webbrowser
			webbrowser.open(link, new=2)	
		else:
			print ("Probably task cloud folder doen't exists")

	def createFeedbackFi(self, pathfileName,projName,contenido):
		fileNa = pathfileName.split('/')[-1]
		#onlyPath = pathfileName.split('/'+fileNa)[0]
		
		
		pathh =	self.pathOnlyBuilt( pathfileName )
		if pathh.endswith('/'):
			partes = pathh.split('/')
			if partes[-1] == '':
				namea = partes[-2]
			else:
				namea = partes[-1]
			ruta =	self.pathOnlyBuilt( pathh )
			#ruta = pathh.split(namea)[0]
			onlyPath = ruta + namea
		else:
			onlyPath = pathh
		
		
		#onlyPath =	self.pathOnlyBuilt( pathfileName )
		self.credenciales = self.login()
		tuplas = self.builtPathSinceRoot ( onlyPath, projName,self.credenciales)
		if tuplas != False:
			idFather = tuplas[1].split('/')[-1]
			query = " '%%%s%%' in parents and trashed=false"%(idFather)
			query = query.replace('%','')
			childrenLs_list = self.credenciales.ListFile({'q':query}).GetList()
			keyExist=False
			objMatching = ''
			for gooObj in childrenLs_list:
				if fileNa.startswith(gooObj['title']):
					keyExist=True
					objMatching = gooObj
			new_permission = {
				'id': 'anyoneWithLink',
				'type': 'anyone',
				'value': 'anyoneWithLink',
				'withLink': True,
				'role': 'reader'
			}
			if keyExist:
				permission = objMatching.auth.service.permissions().insert(fileId=objMatching['id'], body=new_permission, supportsTeamDrives=True).execute(http=objMatching.http)
				import webbrowser
				link = 'https://docs.google.com/document/d/%s/edit' %objMatching['id']
				webbrowser.open(link, new=2)
			else:
				newGooFi = self.credenciales.CreateFile({'title':fileNa, 'shared': True, 'copyRequiresWriterPermission': True, 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', #'text/plan',
													'parents':[{'kind':'drive#fileLink','id':idFather}]})
				newGooFi.SetContentString(contenido)
				newGooFi.Upload(param={'convert': True, 'supportsTeamDrives': True})
				permission = newGooFi.auth.service.permissions().insert(fileId=newGooFi['id'], body=new_permission, supportsTeamDrives=True).execute(http=newGooFi.http)
				import webbrowser
				link = 'https://docs.google.com/document/d/%s/edit' %newGooFi['id']
				webbrowser.open(link, new=2)
		else:
			print ("Probably task cloud folder doen't exists")

	def downLoadContentFolder(self, path, projRoot, parent,
							userSlaId, projSlackId, proccesJson):
		projName = projRoot.split('/')[-1]
		self.credenciales = self.login()
		finalList = []
		for p in path:
			tuplas = self.builtPathSinceRoot ( p, projName, self.credenciales )
			if tuplas != False:
				googPath = tuplas[0]
				googPathId = tuplas[1]
				id = googPathId.split('/')[-1]
				query = " '%%%s%%' in parents and trashed=false "%(id) # and mimeType not contains 'folder'
				query = query.replace('%','')
				childrenLs_list = self.credenciales.ListFile({'q':query}).GetList()
				childrenLs_list2 = []
				doneLs = []
				childrenLs_lsSub = []
				pathdicc={}
				if childrenLs_list != []:
					childrenLs_listFi=[]
					for obj in childrenLs_list:
						if len (obj['mimeType'].split('folder')) < 2:
							if str(obj['id']) not in doneLs:
								childrenLs_listFi.append( str(p+'/'+obj['title']) )
								childrenLs_list2.append(obj)
								pathdicc[str(obj['id'])] = p
								doneLs.append(str(obj['id']))
						else:
							query = " '%%%s%%' in parents and trashed=false "%(str(obj['id'])) # and mimeType not contains 'folder'
							query = query.replace('%','')
							childrenLs_listSubF = self.credenciales.ListFile({'q':query}).GetList()
							for objSubF in childrenLs_listSubF:
								if len (objSubF['mimeType'].split('folder')) < 2:
									if str(objSubF['id']) not in doneLs:
										childrenLs_listFi.append( str(p+'/'+obj['title']+'/'+objSubF['title']) )
										childrenLs_list.append(objSubF)
										pathdicc[str(objSubF['id']) ] = p+'/'+obj['title']
										childrenLs_list2.append(objSubF)
										doneLs.append(str(objSubF['id']))
						
					childrenLs_listFi = childrenLs_listFi + ['bla'] # ,'ble','bli'
					content ='{"fileDoneRefStart" : %s}'%str(childrenLs_listFi).replace("'",'"')
					with open( temp_folder + "/fileDoneRefStart.json" , "w") as file:
						file.write(content)
						file.close()
					for gooObj in childrenLs_list2:
						try:
							if not os.path.exists(pathdicc[str(gooObj['id'])]):
								os.makedirs( pathdicc[str(gooObj['id'])] )
							gooObj.GetContentFile( pathdicc[str(gooObj['id'])]+'/'+ gooObj['title'])
							print ('  --  --  --  --  --  --  ')
							mesnajeBot = "    downloading:    " + pathdicc[str(gooObj['id'])] +'/'+ gooObj['title']
							print (mesnajeBot)
							#print ("que ondeli?")
							self.addItemRef2JsonLs(pathdicc[str(gooObj['id'])]+'/'+gooObj['title'], proccesJson )
							finalList.append( pathdicc[str(gooObj['id'])] +'/'+ gooObj['title'] )
						except Exception as err:
							print (err)
							self.addItemRef2JsonLs('-', proccesJson )
							print (' . ....   .. ... warning try')
							pass
		return finalList

	def listContentFold(self,foldPath,projRoot, parent):
		self.credenciales = self.login()
		tuplas = self.builtPathSinceRoot ( foldPath, projRoot, self.credenciales)
		if tuplas != False:
			idFather = tuplas[1].split('/')[-1]
			query = " '%%%s%%' in parents and trashed=false"%(idFather)
			query = query.replace('%','')
			contentLs = self.credenciales.ListFile({'q':query}).GetList()
			return contentLs
		
	def downContSubFolder(self, foldPath ,  projRoot ,  parent ,
							userSlaId, projSlackId, proccesJson):
		self.credenciales = self.login()
		tuplas = self.builtPathSinceRoot ( foldPath, projRoot, self.credenciales)
		if tuplas != False:
			googleObj = tuplas[2]
			self.dowlo_file( googleObj, foldPath , "", "", True ,True)

	def downlo_toolsCredsOrig(self, pathOnlyPy, pathOnlyCred, projRootNa , userIdSlack, projId, keyButton,proccesJson,ifFolderTools):
		self.projName = projRootNa.split('/')[-1]
		self.credenciales = self.login()
		if len(pathOnlyPy) == 3:
			iconsPath = pathOnlyPy[2]
			shelfPath = pathOnlyPy[1]
		scriptsPath = pathOnlyPy[0]
		#toolsRepoPath = projRootNa +'/PIPELINE/TOOLS'
		#tuplas = self.builtPathSinceRoot ( toolsRepoPath, self.projName,self.credenciales)
		#if tuplas != False:
		if True:
			#idFather = tuplas[1].split('/')[-1]
			query = " '%%%s%%' in parents and trashed=false"%(ifFolderTools)
			query = query.replace('%','')
			lista_toolsGooObj = self.credenciales.ListFile({'q':query}).GetList()
			for obj in lista_toolsGooObj:
				print ('waiting... ' + obj['title'])
			downLoadedLs = []
			if lista_toolsGooObj != []:
				for idx, gooObj in enumerate(lista_toolsGooObj):
					if gooObj['title'] not in downLoadedLs:
						if gooObj['title'].split('.')[-1] in ['json','py','pyc','mel','png','txt','rar']:
							if gooObj['title'].endswith('.png'):
								if len(pathOnlyPy) == 3:
									gooObj.GetContentFile( iconsPath+'/'+gooObj['title'])
									self.addItem2JsonLs(iconsPath+'/'+gooObj['title'], proccesJson )
									downLoadedLs.append(iconsPath+'/'+gooObj['title'])
									print ('  --  --  --  --  --  --  ')
									mesnajeBot = "    downloading:    " + gooObj['title']
									print (mesnajeBot)
									print ("  ")
								else:
									self.addItem2JsonLs(gooObj['title'], proccesJson )
							elif gooObj['title'] == 'shelf_Pr_G.mel':
								if len(pathOnlyPy) == 3:
									name = gooObj['title'].split('.mel')[0]
									try:
										os.remove(shelfPath + '/'+name +'_old_.mel')
									except:
										pass
									import os
									try:
										gooObj.GetContentFile( shelfPath+'/'+gooObj['title'] )
										downLoadedLs.append(shelfPath+'/'+gooObj['title'])
									except Exception as err:
										import glob
										idx = glob.glob(shelfPath + '/'+'shePr_old_*')
										idx = str(len (idx))
										os.rename(shelfPath + '/'+  gooObj['title'],shelfPath + '/'+'shePr_old_%s.txt' %idx )
										try:
											gooObj.GetContentFile( shelfPath+'/'+gooObj['title'] )
										except Exception:
											pass
										downLoadedLs.append(shelfPath+'/'+gooObj['title'])
									print ('  --  --  --  --  --  --  ')
									mesnajeBot = "    downloading:    " + gooObj['title']
									print (mesnajeBot)
									print ("  ")
									self.addItem2JsonLs(shelfPath+'/'+gooObj['title'], proccesJson )
									from stat import S_IREAD, S_IRGRP, S_IROTH
									filename = shelfPath+'/'+gooObj['title']
									os.chmod(filename, S_IREAD|S_IRGRP|S_IROTH)
								else:
									self.addItem2JsonLs(gooObj['title'], proccesJson )
							elif gooObj['title'] in ['client_secrets.json', 'creds.json', 'mycreds.txt']:
								gooObj.GetContentFile( pathOnlyCred + '/'+  gooObj['title'])
								self.addItem2JsonLs(pathOnlyCred+'/'+gooObj['title'], proccesJson )
								downLoadedLs.append(pathOnlyCred+'/'+gooObj['title'])
								print ('  --  --  --  --  --  --  ')
								mesnajeBot = "    downloading:    " + gooObj['title']
								print (mesnajeBot)
								print ("  ")

							elif gooObj['title'].endswith('.py') or gooObj['title'].endswith('.pyc') or gooObj['title'].endswith('.mel'):
								if 'shelf_Pr_G.mel' != gooObj['title']:
									if gooObj['title'] not in downLoadedLs:
										gooObj.GetContentFile( scriptsPath + '/'+  gooObj['title'])
										self.addItem2JsonLs(scriptsPath+'/'+gooObj['title'], proccesJson )
										downLoadedLs.append(scriptsPath+'/'+gooObj['title'])
										print ('  --  --  --  --  --  --  ')
										mesnajeBot = "    downloading:    " + gooObj['title']
										print (mesnajeBot)
										print ("  ")
										if gooObj['title'] == 'googleDrive2Prg.pyc' :
											gooObj.GetContentFile( pythonPath + '/'+  gooObj['title'])
											print( "    downloading:   TestCrash " + gooObj['title'] )
									else:
										self.addItem2JsonLs(gooObj['title'], proccesJson )
							else:
								self.addItem2JsonLs('-', proccesJson )
						else:
							self.addItem2JsonLs('-', proccesJson )
					else:
						self.addItem2JsonLs(gooObj['title'], proccesJson )

			else:
				print ('No Tools on current Project Repository')

		self.addItemRef2JsonLsDone( downLoadedLs , [], proccesJson )
		time.sleep(3)
		try:
			pathh  = os.path.join( temp_folder+'/',proccesJson )
			if os.path.isfile(pathh):
				os.remove(pathh)
		except:
			pass
				
		if keyButton:
			import webbrowser
			webbrowser.open('https://drive.google.com/file/d/1qtgnL4o7muw2xm-ERpQqRiDm8ar_OmR8/view', new=2)	

	def InsertPropVersion(self, ruta_archivo, paternName):
		self.credenciales = self.login()
		resultado = self.buscar ( paternName )
		item= resultado[0]
		self.subir_archivo( ruta_archivo, item['parents'][0]['id'])

	def downLSceneRefOrig(self, tuplaPaths , projRoot, exten, parent, userIdSlack, projId, keyPrint, proccesJson):
		self.projName = projRoot.split('/')[-1]
		wrongPath = ''
		self.wrongPathList = []
		self.credenciales = self.login()
		notMayaFiLs = []
		lista = []
		pathContainerLs = []
		for path in tuplaPaths:
			if not path.endswith(exten):
				if path.endswith('/get_content'):
					pathContainerLs.append(path.split('/get_content')[0])
				else:
					notMayaFiLs.append( path )
		pathVers = tuplaPaths[0]
		lista.append(pathVers)
		doneList = []
		if len(tuplaPaths) > 1:
			pathPubl = tuplaPaths[1]
			lista.append( pathPubl )
			publNa = pathPubl.split('/')[-1]
			#thumbPathMain = pathPubl.split(publNa)[0]
			thumbPathMain =	self.pathOnlyBuilt( pathPubl )
			publNa = publNa.split('_')[0]
			publNa = publNa.split('.')[0]
			thumbPathMain = tuplaPaths[2]
			lista.append( thumbPathMain )
			
		toSearchRefListFi, nonMaya = self.getListForDwAndDw( lista , exten, userIdSlack, projId, self.projName , self.credenciales, 'first' ,keyPrint, proccesJson)
		for fi in nonMaya:
			if fi not in doneList:
				doneList.append(fi)
		if toSearchRefListFi != []:
			key = True
			while key:
				for fi in toSearchRefListFi:
					if not fi.endswith('get_content'):
						if fi not in doneList or pathVers == fi:
							doneList.append(fi)
							if fi.endswith('.ma'):
								content ='{"fileDoneRefStart" : %s}'%str(str([""]))
								with open( temp_folder + "/fileDoneRefStart.json" , "w") as file:
									file.write(content)
									file.close()
								lista ,wrongPathList= self.getRefList (fi , projRoot)
								if lista != []:
									lista2 = []
									for l in lista:
										lista2.append(str(l))
									lista2 = lista2 + ['bla']
									content ='{"fileDoneRefStart" : %s}'%str(lista2).replace("'",'"')
									with open( temp_folder + "/fileDoneRefStart.json" , "w") as file:
										file.write(content)
										file.close()
								for w in wrongPathList:
									self.wrongPathList.append(w)
							if lista != []:
								searchToo =[]
								for f in lista:
									if f.endswith(exten):
										file = f.split('/')[-1]
										if len(file.split('_')) >1:
											if len(file.split('_')) ==4:
												file = file.split('_')[1]
											if len(file.split('_')) ==2:
												file = file.split('_')[0]
											if len(file.split('_')) ==3:
												if not file.split('_')[0].startswith(squencePrefix) and file.split('_')[2].startswith('v'):
													file = file.split('_')[0]
												else:
													file = file.split('_')[1]
										file = file.split('.')[0]
										#assRootPath = f.split(file)[0]
										assRootPath =	self.pathOnlyBuilt( f )
										assRootPath = assRootPath.split(file)[0]+file+'/'

										searchToo.append(assRootPath + 'thumbnailPrg_' + file + '.jpg')
								toSearchRefListFi, nonMaya = self.getListForDwAndDw( lista + searchToo , exten, userIdSlack, projId , self.projName , self.credenciales,'afterFirst', keyPrint, proccesJson)
								for fi in nonMaya:
									if fi not in doneList:
										doneList.append(fi)
								if toSearchRefListFi != []:
									newToSearchRefListFi = []
									for p in toSearchRefListFi:
										if not doneList:
											newToSearchRefListFi.append(p)
									toSearchRefListFi = newToSearchRefListFi
									if toSearchRefListFi != []:
										for fi in toSearchRefListFi:
											if fi not in doneList:
												doneList.append(fi)
									else:
										key = False
								else:
									key = False
							else:
								key = False
								break						
						else:
							key = False
						if toSearchRefListFi == []:
							key = False
							break

			if self.wrongPathList != []:
				wrongPath = "; \nPlease report wrong ProjectRoot Files Setted: " + str(self.wrongPathList)
			else:
				wrongPath = ""
		downLoadNow = []
		for notMFi in notMayaFiLs:
			if notMFi not in doneList:
				downLoadNow.append(notMFi)
		toS, nonMaya = self.getListForDwAndDw( downLoadNow , exten, userIdSlack, projId , self.projName , self.credenciales, 'afterFirst', keyPrint, proccesJson)

		for fi in nonMaya:
			if fi not in doneList:
				doneList.append(fi)

		doneLsAlternat = self.downLoadContentFolder( pathContainerLs, projRoot, parent , "noneSlackCode", 'noprojCode', proccesJson )

		self.addItemRef2JsonLsDone( doneList+doneLsAlternat , self.wrongPathList, proccesJson )
		time.sleep(1)
		try:
			pathh  = os.path.join( temp_folder+'/','fileDoneRefStart.json' )
			if os.path.isfile(pathh):
				os.remove(pathh)
		except:
			pass

	def getListForDwAndDw(self, listaFi, MayaExten , userIdSlack, projId, projName, credenciales, keyOrder, keyPrint ,proccesJson):
		#json
		toSeaRefListFi = []
		nonMayaFiLs = []
		fileDoneLs = []
		for i, f in enumerate( listaFi ):
			gooObjVerLs = []
			listHig = []
			diccId = {}
			fileNaExt = f.split('/')[-1]
			exten = fileNaExt.split('.')[-1]
			exten = '.' + exten
			#pathh = f.split(fileNaExt)[0]
			pathh =	self.pathOnlyBuilt( f )
			if pathh.endswith('/'):
				partes = pathh.split('/')
				if partes[-1] == '':
					namea = partes[-2]
				else:
					namea = partes[-1]
				ruta =	self.pathOnlyBuilt( pathh )
				#ruta = pathh.split(namea)[0]
				onlyPath = ruta + namea
			else:
				onlyPath = pathh
			
			tuplas = self.builtPathSinceRoot ( onlyPath, projName, credenciales)
			if tuplas != False:
				idFather = tuplas[1].split('/')[-1]
				if len( fileNaExt.split('_v') ) > 1:
					fileNa = fileNaExt.split('_v') 
					fileNa = fileNa[0]  + '_'#'_v'
					query = " '%%%s%%' in parents and trashed=false and title contains '%%%s%%'"%(idFather,fileNa)
					query = query.replace('%','')
					dicFileGoodV = credenciales.ListFile({'q':query}).GetList()
					if [] != dicFileGoodV:
						for gooFi in dicFileGoodV:
							if gooFi['title'].endswith(MayaExten):
								if gooFi['title'] not in listHig:
									listHig.append(gooFi['title'])
									diccId[ gooFi['title'] ] = gooFi['id']
									fileNaExt = gooFi['title']
				query = " '%%%s%%' in parents and trashed=false and title contains '%%%s%%'"%(idFather,fileNaExt)
				query = query.replace('%','')
				try:
					dicFileGooD = credenciales.ListFile({'q':query}).GetList()
				except Exception as err:
					dicFileGooD = []
					print (str(err) + '      try   warning')
				if [] != dicFileGooD:
					for gooFi in dicFileGooD:
						if len( gooFi['title'].split('_v') ) > 1 and fileNaExt.endswith(MayaExten):
							listHig = sorted(listHig)
							id = diccId[ listHig[-1] ]
							fileNaExt = listHig[-1]
							for obj in dicFileGoodV:
								if obj['id']==id:
									gooFi = obj
						else:
							id = gooFi['id']
						if not os.path.exists(pathh):
							os.makedirs(pathh)
						if pathh+fileNaExt not in fileDoneLs:
							self.dowlo_file( gooFi , pathh , userIdSlack, projId, True ,keyPrint)
							if keyOrder == 'first':
								self.addItem2JsonLs(pathh+gooFi['title'], proccesJson )
							elif keyOrder ==  'afterFirst':
								self.addItemRef2JsonLs(pathh+gooFi['title'], proccesJson )
							fileDoneLs.append(pathh + fileNaExt )
						if fileNaExt.endswith('.ma'):
							toSeaRefListFi.append (pathh + fileNaExt )
						else:
							nonMayaFiLs.append (pathh + fileNaExt )
				else:
					if f not in fileDoneLs:
						if keyOrder == 'first':
							self.addItem2JsonLs(f, proccesJson )
						elif keyOrder ==  'afterFirst':
							self.addItemRef2JsonLs(f, proccesJson )
						fileDoneLs.append(f )
			else:
				if f not in fileDoneLs:
					if keyOrder == 'first':
						self.addItem2JsonLs(f, proccesJson )
					elif keyOrder ==  'afterFirst':
						self.addItemRef2JsonLs(f, proccesJson )
					fileDoneLs.append(f )
		return (toSeaRefListFi,nonMayaFiLs)

	def getRefList (self, fileForSearcRef , projRoot):
		filePathList=[]
		wrongPathList=[]
		if str(type(fileForSearcRef))== 'list':
			fileForSearcRef = fileForSearcRef[0]
		if fileForSearcRef.endswith('.ma'):
			if fileForSearcRef.startswith (projRoot+'/') or fileForSearcRef.startswith ('/'+projRoot+'/'):
				with open( fileForSearcRef , 'r') as fi:
					fiLinesLsStrings = fi.readlines()
					fi.close()
				for line in fiLinesLsStrings:
					line = line.replace('\\""','')
					if len ( line.split(projRoot+'/') ) > 1:
						filePath= line.split(projRoot+'/')[-1]
						if len(filePath.split(".jpg")) > 1 or len(filePath.split(".ma")) > 1 or len(filePath.split(".tx")) > 1or len(filePath.split(".png")) > 1 or len(filePath.split(".abc")) > 1 or len(filePath.split(".tga")) > 1 or len(filePath.split(".mb")) > 1 or len(filePath.split(".exr")) > 1 or len(filePath.split(".fbx")) > 1:
							filePathh = projRoot+'/'+ filePath.split('";')[0]
							if len(filePathh.split('{')) < 2:
								if filePathh not in (filePathList):
									filePathList.append(filePathh)
					else:
						ignList = ['C:/Program Files/Autodesk/Mudbox 2014/','C:/Program Files/Autodesk/Mudbox 2015/','C:/Program Files/Autodesk/Mudbox 2016/', '.xP:/']
						if len(line.split (ignList[0])) > 1 or len(line.split (ignList[1])) > 1 or len(line.split (ignList[2])) > 1 :
							pass
						else:
							if len( line.split(":/") ) >1:
								filePath=line.split(":/")
								filePath = filePath[0][-1] + ":/" + filePath[-1]
								filePath = filePath.split('";')[0]
								if len(filePath.split(';')) < 2 :
									if len(filePath.split('t\\t\\t')) < 2 :
										if len(filePath.split('\\n')) < 2 :
											wrongPathList.append( filePath )
			else:
				wrongPathList.append( fileForSearcRef )
		return (filePathList,wrongPathList)

	def downLoadCustomOriginal (self, pathList, parent, userIdSlack, projId, projName, signalPrint, proccesJson):
		self.projName = projName
		self.credenciales = self.login()
		doneLs = []
		for p in pathList:
			name = str(p.split('/')[-1])
			#pathRoot = str(p.split(name)[0])
			pathRoot =	self.pathOnlyBuilt( p )
			if pathRoot.endswith('/'):
				partes = pathRoot.split('/')
				if partes[-1] == '':
					namea = partes[-2]
				else:
					namea = partes[-1]
				ruta =	self.pathOnlyBuilt( pathRoot )
				#ruta = pathRoot.split(namea)[0]
				onlyPath = ruta + namea
			else:
				onlyPath = pathRoot
			tuplas = self.builtPathSinceRoot ( onlyPath, self.projName, self.credenciales)
			if tuplas != False:
				idFather = tuplas[1].split('/')[-1]
				query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%' "%(idFather, name)
				query = query.replace('%','')
				dicFileGooD = self.credenciales.ListFile({'q':query}).GetList()
				if [] != dicFileGooD:
					for gooFi in dicFileGooD:
						if pathRoot+gooFi['title'] not in doneLs:
							if not os.path.exists(pathRoot):
								try:
									os.makedirs(pathRoot)
								except Exception:
									#print (gooFi['title'] + '    fallando')
									pass
							try:
								print ('...Downloading  ' + pathRoot+'/'+gooFi['title'])
								gooFi.GetContentFile( pathRoot+gooFi['title'])
							except Exception as err:
								print (err)
								pass
							doneLs.append(pathRoot+gooFi['title'])
							self.addItem2JsonLs(pathRoot+gooFi['title'], proccesJson )
				else:
					try:
						with open( "C:/Python27/freeWhile.json", "w") as fileFa:
							fileFa.write( 'None' )
							fileFa.close()
					except Exception:
						pass
					if pathRoot+name not in doneLs:
						self.addItem2JsonLs(pathRoot+name, proccesJson )
						doneLs.append(pathRoot+name)
			else:
				#print ('no existe ni su carpeta contenedora')
				try:
					with open( "C:/Python27/freeWhile.json", "w") as fileFa:
						fileFa.write( 'None' )
						fileFa.close()
				except Exception:
					pass
				if pathRoot+name not in doneLs:
					self.addItem2JsonLs(pathRoot+name, proccesJson )
					doneLs.append(pathRoot+name)
		time.sleep(1)
		try:
			pathh  = os.path.join( temp_folder+'/',proccesJson )
			if os.path.isfile(pathh):
				os.remove(pathh)
		except:
			pass

	def startwin(self,pathList, parent, userIdSlack, projId, projRoot):
		credenciales = self.login()
		inst = WindowLog(tuplaPaths=pathList , projRoot=projRoot, exten='.ma', userIdSlack=userIdSlack, projId=projId, userNa='bla',credenciales=credenciales)
		#inst.setGeometry(50,50,500,500)
		inst.show()
		return m
		
	def downLastPlay(self, folPathList , parent , exten , userIdSlack, projId ,projName):
		self.projName = projName
		self.keyDone = False
		self.credenciales = self.login()
		for p in folPathList:
			name = p.split('/')[-1]
			#pathRoot = p.split(name)[0]
			pathRoot =	self.pathOnlyBuilt( p )
			if pathRoot.endswith('/'):
				partes = pathRoot.split('/')
				if partes[-1] == '':
					namea = partes[-2]
				else:
					namea = partes[-1]
				ruta =	self.pathOnlyBuilt( pathRoot )
				#ruta = pathRoot.split(namea)[0]
				onlyPath = ruta + namea
			else:
				onlyPath = pathRoot
			tuplas = self.builtPathSinceRoot ( onlyPath, projName,self.credenciales)
			if tuplas != False:
				idFather = tuplas[1].split('/')[-1]
				query = " '%%%s%%' in parents and trashed=false and title contains '%%%s%%' "%(idFather,name)
				query = query.replace('%','')
				dicFileGooD = self.credenciales.ListFile({'q':query}).GetList()			
			
				if [] != dicFileGooD:
					nameVersionsLs = []
					for gooFi in dicFileGooD:
						modifArchivo = gooFi['modifiedDate']
						fechaModGoogFi = modifArchivo.split(".")[0]
						nameVersionsLs.append( fechaModGoogFi )
					orderLs = sorted(nameVersionsLs)
					if not os.path.exists(pathRoot):
						os.makedirs(pathRoot)
					for gooFi in dicFileGooD:
						if gooFi['modifiedDate'].startswith(orderLs[-1]):
							gooFi.GetContentFile( pathRoot + gooFi['title'] )
							print ('  --  --  --  --  --  --  ')
							mesnajeBot = "    downloading:    " + pathRoot + gooFi['title']
							print (mesnajeBot)
							self.slackBot( mesnajeBot, userIdSlack, projId )
							print ("  ")
		import webbrowser
		webbrowser.open('https://drive.google.com/file/d/1qtgnL4o7muw2xm-ERpQqRiDm8ar_OmR8/view', new=2)

	def addItem2JsonLs(self, item, json):
		try:
			with open( temp_folder + "/" + json ) as fi:
				data = fi.readlines()[0]
				dict = ast.literal_eval(data)
				filesDoneLs = dict['filesDone']
				fi.close()
			filesDoneLs.append(item)
			filesDoneLs = str(filesDoneLs).replace("'",'"')
			wrongPathLs = str(dict['wrongPathLs'] ).replace("'",'"')
			fileDoneRef = str(dict['fileDoneRef'] ).replace("'",'"')
			content ='{"filesDone" : %s,"wrongPathLs" : %s,"fileDoneRef" : %s}'%(filesDoneLs,wrongPathLs,fileDoneRef)
			with open( temp_folder + "/" + json , "w") as file:
				file.write(content)
				file.close()
		except Exception:
			pass

	def addItemRef2JsonLs(self, item, json):
		try:
			with open( temp_folder + "/" + json ) as fi:
				data = fi.readlines()[0]
				dict = ast.literal_eval(data)
				filesDoneRefLs = dict['fileDoneRef']
				fi.close()
			filesDoneRefLs.append(item)
			filesDoneRefLs = str(filesDoneRefLs).replace("'",'"')
			wrongPathLs = str(dict['wrongPathLs'] ).replace("'",'"')
			fileDoneLs = str(dict['filesDone'] ).replace("'",'"')
			content ='{"filesDone" : %s,"wrongPathLs" : %s,"fileDoneRef" : %s}'%(fileDoneLs,wrongPathLs,filesDoneRefLs)
			with open( temp_folder + "/" + json , "w") as file:
				file.write(content)
				file.close()
		except Exception:
			pass

	def addItemRef2JsonLsDone(self, allpath , wrongPathLs, proccesJson):
		try:
			with open( temp_folder + "/" + proccesJson ) as fi:
				data = fi.readlines()[0]
				dict = ast.literal_eval(data)
				filesDoneRefLs = dict['fileDoneRef']
				fi.close()
			filesDoneRefLs = str(filesDoneRefLs).replace("'",'"')
			wrongPathLs = str(wrongPathLs ).replace("'",'"')
			fileDoneLs = str('"Done"' ).replace("'",'"')
			content ='{"filesDone" : %s,"wrongPathLs" : %s,"fileDoneRef" : %s, "allpath":%s}'%(fileDoneLs,wrongPathLs,filesDoneRefLs,str(allpath).replace("'",'"'))
			with open( temp_folder + "/" + proccesJson, "w") as file:
				file.write(content)
				file.close()
		except Exception:
			pass
	
	def uploadSceneOrig (self, tuplaPaths, projRootName, parent, userIdSlack, productChanel,projId, userNa, proccesJson):
		self.projName = projRootName.split('/')[-1]
		message = ''
		uploadMessLs = []
		self.wrongPathList = []
		self.credenciales = self.login()
		for fi in tuplaPaths:
			print ('')
		for fi in tuplaPaths:
			name =str(fi.split('/')[-1])
			#pathSinNa=fi.split(str(name))[0]
			pathSinNa = self.pathOnlyBuilt(fi)
			doneLlist = []
			if not os.path.isdir( os.path.join( pathSinNa,name ) ):
				keyAnyExtension = False
				key = False
				name=fi.split('/')[-1]
				#pathAlone = fi.split(name)[0]
				pathAlone= self.pathOnlyBuilt(fi)
				if pathAlone.endswith('/'):
					partes = pathAlone.split('/')
					if partes[-1] == '':
						namea = partes[-2]
					else:
						namea = partes[-1]
					ruta =	self.pathOnlyBuilt( pathAlone )
					#ruta = pathAlone.split(namea)[0]
					onlyPath = ruta + namea
				else:
					onlyPath = pathAlone
				tuplas = self.builtPathSinceRoot ( onlyPath, self.projName,self.credenciales)
				if tuplas != False:
					idFather = tuplas[1].split('/')[-1]
					query = " '%%%s%%' in parents and trashed=false and title = '%%%s%%' "%(idFather,name)
					query = query.replace('%','')
					fileGoo = self.credenciales.ListFile({'q':query}).GetList()
				else:
					fileGoo = []
				if not name.endswith('.ma') or not name.endswith('.mb'):
					key = True
					keyAnyExtension = True
				else:
					key = True
				if key:
					if fileGoo != [] :
						print ('Updating Created file on cloud...')
						keyFind = False
						for gooObj in fileGoo:
							if gooObj not in doneLlist:
								if True:
									if keyAnyExtension:
										if fi not in uploadMessLs:
											gooObj.SetContentFile(fi)
											gooObj.Upload()
											doneLlist.append(fi)
											self.addItem2JsonLs(fi, proccesJson)
											print ('  --  --  --  --  --  --  ')
											print (' Uploading:   ' + str (fi) )
											print ('  ')
											print (' ')
											uploadMessLs.append(fi)
											fileGoo = []
											break
										else:
											if fi not in uploadMessLs:
												self.addItem2JsonLs(fi, proccesJson)
												uploadMessLs.append(fi)
									else:
										if fi not in uploadMessLs:
											keyFind = True
											fechaModGoogFi = gooObj['modifiedDate'].split(".")[0]
											fechaModGoogFi = self.timeFixer(fechaModGoogFi,3)
											tim_local = os.stat(fi).st_mtime
											fecha =time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(fi)))
											hora = time.ctime(os.path.getmtime(fi))
											hora = hora.split(" ")[-2]
											fechaLocalFi = fecha + "T" + hora
												
											gooObj.SetContentFile(fi)
											gooObj.Upload()
											doneLlist.append(fi)
											self.addItem2JsonLs(fi, proccesJson)
											print (' . . . . . . . . ')
											print (fechaLocalFi)
											print ('Local Date')
											print (fechaModGoogFi)
											print ('GoogleD Date')
											print (' . . . . . . . . ')
											print ('  --  --  --  --  --  --  ')
											print (' Uploading:   ' + str (fi))
											print ('  ')
											print (' ')
											uploadMessLs.append(fi)
											fileGoo = []
											break
										else:
											if fi not in uploadMessLs:
												self.addItem2JsonLs(fi, proccesJson)
												uploadMessLs.append(fi)
							else:
								if fi not in uploadMessLs:
									self.addItem2JsonLs(fi, proccesJson)
									uploadMessLs.append(fi)

						if keyFind == False:
							if fi not in uploadMessLs:
								fatherID = self.createPathGooD( fi, projRootName)
								self.subir_archivo( fi, fatherID)
								self.addItem2JsonLs(fi, proccesJson)
								print ('  --  --  --  --  --  --  ')
								print (' Uploading:   ' + str (fi))
								print ("  ")
								print (' ')
								uploadMessLs.append(fi)
							else:
								if fi not in uploadMessLs:
									self.addItem2JsonLs(fi, proccesJson)
									uploadMessLs.append(fi)
						else:
							if fi not in uploadMessLs:
								self.addItem2JsonLs(fi, proccesJson)
								uploadMessLs.append(fi)
					else:
						print ('Creating file...')
						if fi not in uploadMessLs:
							fatherID = self.createPathGooD( fi, projRootName)
							self.subir_archivo( fi, fatherID)
							self.addItem2JsonLs(fi, proccesJson)
							print ('  --  --  --  --  --  --  ')
							print (' Uploading:   ' + str (fi))
							print ("  ")
							print ('')
							uploadMessLs.append(fi)
						else:
							if fi not in uploadMessLs:
								self.addItem2JsonLs(fi, proccesJson)
								uploadMessLs.append(fi)
			else:
				if fi not in uploadMessLs:
					print ('File Doesn t exists')
					self.addItem2JsonLs(pathSinNa+name, proccesJson)
					uploadMessLs.append(fi)
		time.sleep(2)
		try:
			pathh  = os.path.join( temp_folder+'/', proccesJson )
			if os.path.isfile(pathh):
				os.remove(pathh)
		except:
			pass
			
		if self.wrongPathList != []:
			wrongPath = "; Please report wrong ProjectRoot Files Setted: " + str(self.wrongPathList)
		else:
			wrongPath = ''
		if message != '':
			header = ' Uploading Files Done '
		elif len (message.split('already updated')) > 1:
			header = ' Uploading Exception '
		else:
			header = ' Uploading Warning '
		if uploadMessLs != []:
			mesnajeBot = '   '+ userNa + ' is Uploading File/s  on Cloud Repository:      \n' + str(uploadMessLs) + '\n\n'
			self.slackBot( mesnajeBot, productChanel, projId )
			self.slackBot( mesnajeBot, userIdSlack, projId )


	def timeFixer( self, fechaModGoogFi, timeOffset):
		partes = fechaModGoogFi.split("T")
		hora = partes[-1]
		fecha = partes[0]
		partesHora =  hora.split(':')
		partesFecha = fecha.split('-')
		fixH = int(partesHora[0]) - timeOffset
		if fixH < 0:
			partesHora[0] = str (24 + fixH)
			fixD = int(partesFecha[2]) - 1
			if fixD == 0:
				mesAnterior = str(int(partesFecha[1]) - 1)
				if len(mesAnterior) == 1:
					mesAnterior = '0' + mesAnterior
					if mesAnterior == '00':
						mesAnterior = '12'
				if mesAnterior in ['04', '06', '09' , '11']:
					finDeMesAnt = 30
				elif mesAnterior in ['01', '03', '05', '07', '08', '10' , '12']:
					finDeMesAnt = 31
				elif mesAnterior == '02':
					bisiestos = ['2024', '2028', '2032', '2036', '2040', '2044', '2048','2052', '2056', '2060']
					if partesFecha[0] not in bisiestos:
						finDeMesAnt = 28
					else:
						finDeMesAnt = 29
				partesFecha[2] = str(finDeMesAnt)
				if partesFecha[2] == str(finDeMesAnt):
					partesFecha[1] = int(partesFecha[1]) - 1
					if partesFecha[1] == 0:
						partesFecha[1] = '12'
						partesFecha[0] = int(partesFecha[0]) - 1
			else:
				partesFecha[2] = int(partesFecha[2]) - 1
			if partesFecha[1] == 0:
				partesFecha[0] == int(partesFecha[0]) - 1
		else:
			partesHora[0] = str (fixH)

		if len (str(partesHora[0])) == 1:
			partesHora[0] = '0'+ str(partesHora[0])
		if len (str(partesFecha[1])) == 1:
			partesFecha[1] = '0'+ str(partesFecha[1])
		if len (str(partesFecha[0])) == 1:
			partesFecha[0] = '0'+ str(partesFecha[0])
		return str(partesFecha[0]) + '-' + str(partesFecha[1]) + '-' + str(partesFecha[2]) + 'T'+ str(partesHora[0]) + ':' + str(partesHora[1]) + ':' + str(partesHora[2])

