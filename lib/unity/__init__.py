import unitypack
from unitypack.asset import Asset
from unitypack.export import OBJMesh
from unitypack.utils import extract_audioclip_samples

from io import BytesIO

class UnityAssetBundle:

	FORMAT_ARGS = {
		"audio": "AudioClip",
		"fonts": "Font",
		"images": "Texture2D",
		"models": "Mesh",
		"shaders": "Shader",
		"text": "TextAsset",
		"video": "MovieTexture",
	}

	def __init__(self, basePath="./out/"):
		self.bundleLoaded = False
		self.handle_formats = []
		self.basePath = basePath
		for a, classname in self.FORMAT_ARGS.items():
			self.handle_formats.append(classname)
		pass

	def setBundleByPath(self, path : str):
		self.bundleLoaded = True
		self.path = path
		self.unityBundle = unitypack.load(open(path, "rb"))
		self.prepareBundle()
		pass

	def setBundleByFile(self, file):
		self.bundleLoaded = True
		self.unityBundle = unitypack.load(file)
		self.prepareBundle()
		pass
		
	def prepareBundle(self):
		self.unityAssetBundles = self.unityBundle.assets
		pass

	def getAssetsList(self):
		if not self.bundleLoaded:
			raise Exception("Bundle is not loaded. Load with setBundleByPath or setBundleByFile")

		for asset in self.unityBundle.assets:
			return self.extractAssetBundle(asset, False)

		return []

	def extractAssets(self):
		if not self.bundleLoaded:
			raise Exception("Bundle is not loaded. Load with setBundleByPath or setBundleByFile")

		for asset in self.unityBundle.assets:
			return self.extractAssetBundle(asset, True)

		return []

	def get_output_path(filename):
		return self.basePath + filename

	def write_to_file(self, filename, contents, mode="w"):
		path = self.get_output_path(filename)
		with open(path, mode) as f:
			written = f.write(contents)
		print("Written %i bytes to %r" % (written, path))

	def extractAssetBundle(self, asset, extractFlag=True):

		outputPaths = []

		for id, obj in asset.objects.items():
			if obj.type not in self.handle_formats:
				continue

			d = obj.read()

			temp = {
				"type": obj.type,
				"filename": [],
				"size": []
			}

			if obj.type == "AudioClip":
				samples = extract_audioclip_samples(d)
				
				for filename, sample in samples.items():
					temp['filename'].append(filename)
					temp['size'].append(sample.__len__())
					if extractFlag:
						self.write_to_file(filename, sample, mode="wb")

			elif obj.type == "MovieTexture":
				filename = d.name + ".ogv"
				temp['filename'].append(filename)
				temp['size'].append(d.movie_data.__len__())
				if extractFlag:
					self.write_to_file(filename, d.movie_data, mode="wb")

			elif obj.type == "Shader":
				temp['filename'].append(d.name)
				temp['size'].append(d.script.__len__())
				if extractFlag:
					self.write_to_file(d.name + ".cg", d.script)

			elif obj.type == "Mesh":
				temp['filename'].append(d.name)
				try:
					mesh_data = OBJMesh(d).export()
					if extractFlag:
						self.write_to_file(d.name + ".obj", mesh_data, mode="w")
				except NotImplementedError as e:
					print("WARNING: Could not extract %r (%s)" % (d, e))
					mesh_data = pickle.dumps(d._obj)
					if extractFlag:
						self.write_to_file(d.name + ".Mesh.pickle", mesh_data, mode="wb")
				temp['size'].append(mesh_data.__len__())

			elif obj.type == "Font":
				temp['filename'].append(d.name)
				temp['size'].append(d.data.__len__())
				if extractFlag:
					self.write_to_file(d.name + ".ttf", d.data, mode="wb")

			elif obj.type == "TextAsset":
				if isinstance(d.script, bytes):
					filename, mode = d.name + ".bin", "wb"
				else:
					filename, mode = d.name + ".txt", "w"
				temp['filename'].append(d.name)
				temp['size'].append(d.script.__len__())
				if extractFlag:
					self.write_to_file(filename, d.script, mode=mode)

			elif obj.type == "Texture2D":
				filename = d.name + ".png"
				try:
					from PIL import ImageOps
				except ImportError:
					print("WARNING: Pillow not available. Skipping %r." % (filename))
					continue
				try:
					image = d.image
				except NotImplementedError:
					print("WARNING: Texture format not implemented. Skipping %r." % (filename))
					continue

				if image is None:
					print("WARNING: %s is an empty image" % (filename))
					continue
				
				print("Decoding %r" % (d))
				# Texture2D objects are flipped
				img = ImageOps.flip(image)
				output = BytesIO()
				img.save(output, format="png")
				temp['filename'].append(d.name)
				temp['size'].append(output.getvalue().__len__())
				
				if extractFlag:
					self.write_to_file(filename, output.getvalue(), mode="wb")
			else:
				continue
			outputPaths.append(temp)
			pass
		return outputPaths
	pass