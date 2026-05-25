module.exports = {
  modeConfig: {
    basic-dev-mode: {
      id: 'basic-dev-mode',
      routeName: 'basic-dev-mode',
      displayName: 'Basic Development Mode',
      description: 'A basic mode for viewing DICOM studies with MPR and 3D views',
      implementation: 'basic-dev-mode',
      extensions: ['cornerstone'],
      hangingProtocolId: 'mprAnd3DVolumeViewport',
      onModeEnter: ({ extensionManager, servicesManager }) => {
        console.log('Basic Dev Mode entered');
      },
    },
  },
  extensionsConfig: {
    cornerstone: {
      viewportTypes: ['volume', 'stack'],
      synchronization: {
        tool: {
          enabled: true,
          strategies: ['default'],
        },
      },
    },
  },
};