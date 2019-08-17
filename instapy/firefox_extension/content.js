var customScript = `
// Overwrite the contents of the body.
Object.defineProperty(navigator, 'webdriver', {
  get: () => false,
});

// -- overwrite the languages property to use a custom getter
Object.defineProperty(navigator, 'languages', {
  get: () => ['en-US', 'en'],
});

// -- overwrite the plugins property to use a custom getter
Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3, 4, 5],
});

// -- mock webgl renderer
var getParameter = WebGLRenderingContext.getParameter;
WebGLRenderingContext.prototype.getParameter = parameter => {
  // UNMASKED_VENDOR_WEBGL
  if (parameter === 37445) {
    return 'Intel Open Source Technology Center';
  }
  // UNMASKED_RENDERER_WEBGL
  if (parameter === 37446) {
    return 'Mesa DRI Intel(R) Ivybridge Mobile ';
  }

  return getParameter(parameter);
};

// -- mock image size = 0
['height', 'width'].forEach(property => {
  // store the existing descriptor
  var imageDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, property);

  // redefine the property with a patched descriptor
  Object.defineProperty(HTMLImageElement.prototype, property, {
    ...imageDescriptor,
    get: () => {
      // return an arbitrary non-zero dimension if the image failed to load
      if (this.complete && this.naturalHeight == 0) {
        return 20;
      }
      // otherwise, return the actual dimension
      return imageDescriptor.get.apply(this);
    },
  });
});

// -- pass permissions test
var originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = parameters => (
  parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);
`;

document.arrive('head', () => {
  var script = document.createElement('script');
  script.innerHTML = customScript;
  script.type = 'text/javascript';
  document.head.insertBefore(script, document.head.children[0]);
});
