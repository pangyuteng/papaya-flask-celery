window.config = {
  router: {
    basename: '/',
  },
  extensions: [
    {
      id: 'cornerstone',
      version: '4.x',
    },
  ],
  modes: [
    {
      id: 'basic-dev-mode',
      routeName: 'basic-dev-mode',
      dataSourceConfig: {
        type: 'dicomweb',
        configuration: {
          wadoUri: 'http://localhost:5000/dicomweb',
          qidoUri: 'http://localhost:5000/dicomweb',
          wadoRoot: 'http://localhost:5000/dicomweb',
          supportBulkDataURI: false,
          singlepart: true,
        },
      },
      hangingProtocolId: 'mprAnd3DVolumeViewport',
      displaySets: [
        {
          id: 'default',
          default: true,
        },
      ],
      lifecycleHooks: {
        onModeEnter: ({ extensionManager, servicesManager }) => {
          console.log('Basic Dev Mode entered');
        },
      },
    },
  ],
  hotkeys: [
    {
      commandName: 'incrementActiveViewport',
      keys: ['right'],
    },
    {
      commandName: 'decrementActiveViewport',
      keys: ['left'],
    },
  ],
  defaultMode: 'basic-dev-mode',
};

// Override for Docker environment
if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
  window.config.modes[0].dataSourceConfig.configuration = {
    wadoUri: 'http://backend:5000/dicomweb',
    qidoUri: 'http://backend:5000/dicomweb',
    wadoRoot: 'http://backend:5000/dicomweb',
    supportBulkDataURI: false,
    singlepart: true,
  };
}