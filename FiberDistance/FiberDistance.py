import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# FiberDistance
#

class FiberDistance:
  def __init__(self, parent):
    parent.title = "FiberDistance" # TODO make this more human readable by adding spaces
    parent.categories = ["Diffusion.Tractography"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is a scripted module to calculate distance metrics on fibers
    """
    parent.acknowledgementText = """
    This file was originally developed by Steve Pieper, Isomics, Inc.  and was partially funded by NIH grant 3P41RR013218-12S1.
    Based on initial work by Laurent Chauvin and Sonia Pujol of BWH.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['FiberDistance'] = self.runTest

  def runTest(self):
    tester = FiberDistanceTest()
    tester.runTest()

#
# qFiberDistanceWidget
#

class FiberDistanceWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "FiberDistance Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #

    # Collapsible button
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "A collapsible button"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the parameters collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # fibers to compare
    self.fiber1Selector = slicer.qMRMLNodeComboBox(parametersCollapsibleButton)
    self.fiber1Selector.nodeTypes = ( ("vtkMRMLFiberBundleNode"), "" )
    self.fiber1Selector.selectNodeUponCreation = False
    self.fiber1Selector.addEnabled = False
    self.fiber1Selector.removeEnabled = False
    self.fiber1Selector.noneEnabled = True
    self.fiber1Selector.showHidden = False
    self.fiber1Selector.showChildNodeTypes = False
    self.fiber1Selector.setMRMLScene( slicer.mrmlScene )
    self.fiber1Selector.setToolTip( "Pick the first fiber bundle to be compared." )
    parametersFormLayout.addRow("Fiber Bundle 1", self.fiber1Selector)

    # fibers to compare
    self.fiber2Selector = slicer.qMRMLNodeComboBox(parametersCollapsibleButton)
    self.fiber2Selector.nodeTypes = ( ("vtkMRMLFiberBundleNode"), "" )
    self.fiber2Selector.selectNodeUponCreation = False
    self.fiber2Selector.addEnabled = False
    self.fiber2Selector.removeEnabled = False
    self.fiber2Selector.noneEnabled = True
    self.fiber2Selector.showHidden = False
    self.fiber2Selector.showChildNodeTypes = False
    self.fiber2Selector.setMRMLScene( slicer.mrmlScene )
    self.fiber2Selector.setToolTip( "Pick the second fiber bundle to be compared." )
    parametersFormLayout.addRow("Fiber Bundle 2 ", self.fiber2Selector)

    # apply
    self.applyButton = qt.QPushButton(parametersCollapsibleButton)
    self.applyButton.text = "Apply"
    parametersFormLayout.addWidget(self.applyButton)

    self.applyButton.connect('clicked()', self.onApply)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApply(self):
    logic = FiberDistanceLogic()
    print("Run the algorithm")
    logic.run(self.fiber1Selector.currentNode(), self.fiber2Selector.currentNode())

  def onReload(self,moduleName="FiberDistance"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

  def onReloadAndTest(self,moduleName="FiberDistance"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# FiberDistanceLogic
#

class FiberDistanceLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def hausdorffDistance(self,fiber1,fiber2):
    """
    Run the actual algorithm
    """
    return True


class FiberDistanceTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_FiberDistance1()

  def test_FiberDistance1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    #
    # first, get the data
    # - amount of data depends on useCase attribue
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5768', 'tract1.vtk', slicer.util.loadFiberBundle),
        ('http://slicer.kitware.com/midas3/download?items=5769', 'tract2.vtk', slicer.util.loadFiberBundle),
        )
    tracts = ('tract1', 'tract2',)
    tractColors = ( (0.2, 0.9, 0.3), (0.9, 0.3, 0.3),)

    # perform the downloads if needed, then load
    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        self.delayDisplay('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        self.delayDisplay('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    tract1 = slicer.util.getNode('tract1')
    tract2 = slicer.util.getNode('tract2')

    logic = FiberDistanceLogic()
    self.assertTrue( logic.hausdorffDistance(tract1, tract2) )
    self.delayDisplay('Test passed!')