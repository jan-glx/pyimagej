# Known Limitations

For technical reasons, there are some aspects of ImageJ and ImageJ2 that cannot fully work from a Python script:

## The original ImageJ API is limited in headless mode

Normally, the [original ImageJ](https://imagej.net/software/imagej) does not work headless at all. But thanks to [ImageJ2's runtime patching mechanism](https://imagej.net/libs/imagej-legacy), most aspects of the original ImageJ work in [headless mode](https://imagej.net/learn/headless), including via PyImageJ when initializing with `imagej.init(mode=Mode.HEADLESS)`.

That said, there are a couple of major areas of functionality in the original ImageJ that do not work headless, and therefore do not work headless via PyImageJ.

### ROI Manager

ImageJ's [ROI Manager](https://imagej.nih.gov/ij/docs/guide/146-30.html#fig:The-ROI-Manager) allows you to work with multiple regions of interest (ROIs) simultaneously. The `ij.plugin.frame.RoiManager` class is the API for controlling these features. As one might guess just from its package name, `ij.plugin.frame.RoiManager` is a `java.awt.Frame`, and therefore cannot be used headless.

If you need to work with multiple `ij.gui.Roi` objects, one option that works headless is to group them using an `ij.gui.Overlay`.

### WindowManager

ImageJ's `ij.WindowManager` class consists of static functions for working with Java AWT windows, including ImageJ's `ij.gui.ImageWindow`. Each ImageJ image is an `ij.ImagePlus` linked to a corresponding `ij.gui.ImageWindow`. However, in headless mode, there are no image windows, because they cannot exist headless. Therefore, attempts to use the functions of the `WindowManager` will fail, with functions like `WindowManager.getCurrentWindow()` always returning null. Unfortunately, ImageJ tracks open images via their windows; therefore, you cannot know which images have previously been opened while running headless, nor is there an "active image window" while running headless because _there are no windows_.

Note that if you are having problems with a `null` or incorrect active image while **running in `GUI` or `INTERACTIVE` mode (i.e. not `HEADLESS`)**, you might need to call `ij.py.sync_image(imp)`, where `imp` is the `ij.ImagePlus` you want to register or update.

## Non-blocking INTERACTIVE mode on macOS

On macOS, the Cocoa event loop needs to be started from the main thread before any Java-AWT-specific functions can work. And doing so blocks the main thread. For this reason, PyImageJ includes two graphical modes, `GUI` and `INTERACTIVE`, with `GUI` blocking the `imagej.init` invocation, and `INTERACTIVE` returning immediately... but `INTERACTIVE` cannot work on macOS and is therefore not available, due to this OS-specific limitation.

## Old versions of ImageJ2

PyImageJ uses some functions of ImageJ2 and supporting libraries that are not available in older versions of ImageJ2. While it may be possible to initialize an ImageJ2 gateway with an older version of ImageJ2, certain functionality may not behave as intended, so we advise to use version 2.3.0 or later if possible.

## Starting Python from inside ImageJ

At the time of this writing, in order to use PyImageJ, you must start Python first, and initialize ImageJ2 from there.

We have plans to make it possible to go the other direction: starting ImageJ2 as usual and then calling Python scripts for the Script Editor. But this architecture is not complete yet; see [this forum discussion](https://forum.image.sc/t/fiji-conda/59618/11) for details.

# Common Errors

## Error in "mvn.CMD -B -f pom.xml" dependency:resolve: 1

This indicates a problem running Maven on your system and will require more
debugging effort. Please post [on the
forum](https://forum.image.sc/tag/pyimagej) and include either:

* The results of manually running the Maven command with an added `-X` flag: `path\to\mvn.CMD -B -f -X path\to\pom.xml`
* The results of re-running the same `imagej.init` call after:
   * Deleting your `~/.jgo` directory
   * Adding `import logging` and `logging.basicConfig(level = logging.DEBUG)` to the top of your script

### Could not transfer artifact

If the debugging output includes notices such as:
```
DEBUG:jgo: [ERROR] Non-resolvable import POM: Could not transfer artifact net.imglib2:imglib2-imglyb:pom:1.0.1 from/to scijava.public (https://maven.scijava.org/content/groups/public): Transfer failed for https://maven.scijava.org/content/groups/public/net/imglib2/imglib2-imglyb/1.0.1/imglib2-imglyb-1.0.1.pom @ line 8, column 29: Connect to maven.scijava.org:443 [maven.scijava.org/144.92.48.199] failed: Connection timed out:
```
This suggests you may be behind a firewall that is preventing Maven from downloading the necessary components. In this case you have a few options to try:
1. Configure your proxy settings directly in your python code
   ```
   import scyjava
   import imagej
   
   ij = imagej.init() # it is crutial to run this before importing "java.lang.System" such that pyimagej (and not scyjava alone) initializes the JVM
   System = scyjava.jimport('java.lang.System')
   
   # instruct the JVM to use the sytem proxy:
   System.setProperty("java.net.useSystemProxies", "true");
   
   # *alternatively*, manually configure a different proxy:
   mydomain = "myproxy.domain" # replace by your actual proxy
   myport = "8080" # replace by your proxy's actual port, e.g. 80
   System.setProperty("http.proxyHost", mydomain)
   System.setProperty("http.proxyPort", myport)
   System.setProperty("https.proxyHost", mydomain)
   System.setProperty("https.proxyPort", myport)
   ```
2. Configure your proxy settings [through Maven](https://www.baeldung.com/maven-behind-proxy) in the `<settings>..</settings>` block of your `$HOME\.m2\settings.xml` file
   ```
   <proxies>
     <proxy>
       <id>Your company proxy</id>
       <active>true</active>
       <protocol>https</protocol>
       <host>proxy.mycompany.com</host>
       <port>8080</port>
     </proxy>
   </proxies>
   ```
3. Initialize with a local `Fiji.app` installation. In this case you will also have to manually download the latest `.jar` files for [imglib2-unsafe](https://maven.scijava.org/#nexus-search;quick~imglib2-unsafe) and [imglib2-imglyb](https://maven.scijava.org/#nexus-search;quick~imglib2-imglyb) and place them in your local `Fiji.app/jars` directory, as these are required for PyImageJ but not part of the standard Fiji distribution.

### Unable to find valid certification path

If the debugging output includes notices such as:
```
Caused by: sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
    at sun.security.validator.PKIXValidator.doBuild (PKIXValidator.java:397)
    at sun.security.validator.PKIXValidator.engineValidate (PKIXValidator.java:240)
```
This suggests the version of Java being used is too old and contains outdated certificate information. This behavior has been confirmed with the `openjdk` installed from the default conda channel (i.e. `conda install openjdk`). Try using an openjdk from the [conda-forge channel](https://anaconda.org/conda-forge/openjdk) instead.

## I ran a plugin and see an updated image, but the numpy array and dataset are unchanged.

This bug can occur in certain circumstances when using original ImageJ plugins
which update a corresponding `ImagePlus`. It can be worked around by calling:

```python
imp = ij.WindowManager.getCurrentImage()
ij.py.sync_image(imp)
```

## Original ImageJ classes not found

If you try to load an original ImageJ class (with package prefix `ij`),
and get a `JavaException: Class not found` error, this is because
the environment was initialized without the original ImageJ included.
See [Initialization.md](Initialization.md).

## Not enough memory

You can increase the memory available to the JVM before starting it.
See [Initialization.md](Initialization.md).

## log4j:WARN 

PyImageJ does not currently ship a log4j implementation, which results in an
obnoxious warning at startup:

```
log4j:WARN No appenders could be found for logger (org.bushe.swing.event.EventService).
log4j:WARN Please initialize the log4j system properly.
log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
```

This can safely be ignored and will be addressed in a future patch.

## TypeError: No matching overloads

Java has method overloading, whereas Python does not. The JPype library is very
smart about figuring which Java method you intend to call based on the argument
types. But it is not perfect&mdash;see e.g.
[jpype-project/jpype#844](https://github.com/jpype-project/jpype/issues/844).
Therefore, you might encounter an error `TypeError: No matching overloads` when
trying to call certain Java methods in some scenarios. Here is an example:

```python
>>> ij = imagej.init()
>>> ij.op().create()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: No matching overloads found for org.scijava.plugin.PTService.create(), options are:
	public default org.scijava.plugin.SciJavaPlugin org.scijava.plugin.PTService.create(java.lang.Class)
```

Until JPype is improved, you will need to work around the issue case by case.
For example, to avoid the error above with the `create()` method, you can use:

```python
CreateNamespace = imagej.sj.jimport('net.imagej.ops.create.CreateNamespace')
create = ij.op().namespace(CreateNamespace)
```

And then `create` will contain the same object normally accessed via
`ij.op().create()`.

If you are stuck, please post a topic on the [Image.sc Forum](https://forum.image.sc/).
