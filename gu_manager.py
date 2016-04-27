import gu_gitcontroller as gc

CORFRAMEWORK = "https://github.com/bahusvel/COR-Framework"
CORCLI = "https://github.com/bahusvel/COR-CLI.git"
CORINDEX = "https://github.com/bahusvel/COR-Index.git"
CORFRAMEWORK_REPO_ID = "bahusvel/COR-Framework"

CORCLISTORAGE = click.get_app_dir("COR CLI")
STORAGEINDEX = CORCLISTORAGE+"/index"
STORAGE_LOCAL_INDEX = CORCLISTORAGE+"/localindex"
STORAGEMODULES = STORAGEINDEX+"/modules"

def publish():
	entity_location = os.getcwd()
	if check_for_cor():
		username = gc.github_login().get_user().login
		sync_backend()
		remote = gc.getremote()
		localindex = gc.get_cor_index()
		if localindex is None:
			localindex = gc.fork_on_github("bahusvel/COR-Index")
		if not os.path.exists(STORAGE_LOCAL_INDEX):
			os.chdir(CORCLISTORAGE)
			gc.gitclone(localindex.clone_url, aspath="localindex")
		os.chdir(STORAGE_LOCAL_INDEX)
		gc.gitpull()
		# create corfile here
		local_cordict = read_corfile(entity_location + "/.cor/corfile.json")
		local_cordict["repo"] = remote
		if local_cordict["type"] == "MODULE":
			prefix = "modules"
		elif local_cordict["type"] == "FRAMEWORK":
			prefix = "frameworks"
		else:
			raise Exception(local_cordict["type"] + "is an invalid type")
		public_name = local_cordict["name"].lower()
		public_corfile_path = STORAGE_LOCAL_INDEX+"/" + prefix + "/" + public_name + ".json"
		write_corfile(local_cordict, public_corfile_path)
		gc.gitadd(public_corfile_path)
		gc.gitcommit("Added " + public_name)
		gc.gitpush()
		try:
			gc.github_pull_request(localindex.full_name, username, "COR-Index", "Add " + public_name)
		except Exception:
			click.secho("Pull request failed, please create one manualy", err=True)
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)
		

def get_module(url):
	#if get_type() == TYPE.RECIPE:
		# add module to recipe correctly
	#	pass
	gc.gitclone(url)
	
	
def module_corfile(name, language_url):
	if check_for_cor():
		cordict = {"name": name, "type": TYPE.MODULE, "language": language_url}
		cdir = os.getcwd()
		write_corfile(cordict, cdir + "/.cor/corfile.json")

def search_backend(term, searchtype="QUICK", entity_type=TYPE.MODULE):
	if searchtype == "QUICK":
		items = list_type(entity_type)
		return list(filter(lambda x: term in x, items))
	elif searchtype == "FULL":
		pass
	else:
		raise Exception("Invalid search method " + searchtype)

def sync_backend():
	commited = False
	if check_for_cor():
		if gc.getremote() != "":
			if gc.isdiff():
				if click.confirm("You have modified the module do you want to commit?"):
					msg = click.prompt("Please enter a commit message")
					gc.gitupsync(msg)
					commited = True
			gc.gitpull()
			if commited:
				gc.gitpush()
		else:
			click.secho("You do not have git remote setup", err=True)
			if click.confirm("Do you want one setup automatically?"):
				gc.github_login()
				name = read_corfile(os.getcwd() + "/.cor/corfile.json")["name"]
				remote = gc.github_create_repo(name).clone_url
			else:
				click.secho("You will have to create a repository manually and provide the clone url")
				remote = click.prompt("Please enter the url")
			gc.addremote(remote)
			gc.gitadd(".")
			gc.gitcommit("Initlizaing repo")
			gc.gitpush(create_branch=True)
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)


def get_module(name, url):
	if name is None and url is None:
		name = click.prompt("Enter the module name")
	if name is not None and url is None:
		file = STORAGEINDEX+"/modules/"+name+".json"
		if os.path.exists(file):
			cordict = read_corfile(file)
			url = cordict["repo"]
		else:
			click.secho("The module you requested is not in the index", err=True)
			url = click.prompt("Please enter the url for the module")
	if url is not None:
		gc.gitclone(url)


def update(new_index):
	if new_index is not None:
		shutil.rmtree(STORAGEINDEX)
	if not os.path.exists(CORCLISTORAGE):
		os.mkdir(CORCLISTORAGE)
	if not os.path.exists(STORAGEINDEX):
		os.chdir(CORCLISTORAGE)
		if new_index is not None:
			gc.gitclone(new_index, aspath="index")
		else:
			gc.gitclone(CORINDEX, aspath="index")
	else:
		os.chdir(STORAGEINDEX)
		gc.gitpull()

def upgrade(local):
	if not os.path.exists(CORCLISTORAGE):
		os.mkdir(CORCLISTORAGE)
	if not local:
		if not os.path.exists(CORCLISTORAGE+"/cli"):
			os.chdir(CORCLISTORAGE)
			gc.gitclone(CORCLI, aspath="cli")
		os.chdir(CORCLISTORAGE+"/cli")
		gc.gitpull()
	if not local:
		os.system("pip install --upgrade .")
	else:
		os.system("pip install --upgrade --editable .")
