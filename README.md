# HCSvLab RoboChef #

## Installation ##

```
git clone git@github.com:IntersectAustralia/hcsvlab_robochef.git
```

## Install the Dependencies ##

### OS X ###

These instructions assume you have [Homebrew](http://mxcl.github.com/homebrew/) installed


#### AntiWord ####

```
brew install antiword
```

Unfortunately, Homebrew doesn't install the resources correctly so you will have to fix this manually:

```
mv /usr/local/share/antiword/Resources/* /usr/local/share/antiword
rmdir /usr/local/share/antiword/Resources
```

#### Xpdf ####

```
brew install xpdf
```

### CentOS ###

Firstly, if you have not done so already, you will need to enable the [EPEL repository](http://fedoraproject.org/wiki/EPEL). The easiest way is to install the latest appropriate RPM for you version and architecture from [here](http://dl.fedoraproject.org/pub/epel/), eg:

```
$ curl -O http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
$ sudo rpm -Uvh epel-release-6-8.noarch.rpm
```

#### AntiWord and Xpdf ####

```
$ sudo yum install antiword xpdf
```

#### Python 2.7 ####

Enter the following into the command line:

```
$ python -V
```

If it tells you that you have anything other than 2.7 installed, you will need to compile it from source by following these steps.

##### Install the Development Tools #####

```
$ sudo yum groupinstall 'Development tools'
$ sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel

```

##### Download Build and Install Python 2.7 #####

```
$ curl -O http://python.org/ftp/python/2.7.5/Python-2.7.5.tgz
$ tar xvf Python-2.7.5.tgz
$ cd Python-2.7.5
$ ./configure --prefix=/usr/local
$ sudo make && sudo make altinstall
```

You will make your life a million times easier if you also install VirtualEnv

##### SetupTools and VirtualEnv #####

```
$ curl -O https://pypi.python.org/packages/source/s/setuptools/setuptools-0.7.2.tar.gz
$ tar xvf setuptools-0.7.2.tar.gz 
$ cd setuptools-0.7.2
$ sudo /usr/local/bin/python2.7 ez_setup.py 
$ sudo /usr/local/bin/easy_install-2.7 virtualenv
```

Next, create a VirtualEnv for RoboChef in its directory:

```
$ virtualenv hcsvlab_robochef/
$ cd hcsvlab_robochef/
$ source bin/activate
```

## Install the Python Libraries ##

Use [pip](http://www.pip-installer.org/) or [easy_install](https://pypi.python.org/pypi/setuptools) to install `pyparsing`, `xlrd`, and `rdflib`, e.g:

```
pip install "pyparsing<=1.5.7" xlrd "rdflib<=3.4.0" httplib2
```

NOTE: `pyparsing` currently defaults to v2.0 which only works with Python 3

NOTE: `rdflib` versions higher than 3.4.0 have given us errors when processing Paradisec

## Generating RDF with HCSvLab RoboChef ##

Edit the `config.ini` file to point to the corpora and the desired output directory, e.g:

```
CORPUS_BASEDIR = /Users/ilya/workspace/corpora/
CORPUS_OUTPUTDIR = /Users/ilya/workspace/corpora_processed/
```

Add the `hcsvlab_robochef` parent directory to your `PYTHONPATH`, e.g:

```
export PYTHONPATH=$PYTHONPATH:/Users/ilya/workspace/
```

Run `main.py` in the `hcsvlab_robochef` directory:

```
python main.py
```
