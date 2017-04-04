# ABF data incubator

Here is the [finished website served from Heroku.](https://hard-drive.herokuapp.com/)

 * Uses the [conda buildpack](https://github.com/kennethreitz/conda-buildpack). In particular, the command 'heroku config:add BUILDPACK_URL=https://github.com/kennethreitz/conda-buildpack.git' or is this the way: 'heroku buildpacks:add https://github.com/kennethreitz/conda-buildpack.git'


### Intrusctions for deploy:

	1. Beging by creating an empty heroku app on heroku.com with some name
	2. On your command line in this web directoy login to your heroku `heroku login
	3. Set the origin `heroku git:remote -a your-heroku-app-name`
	4.



