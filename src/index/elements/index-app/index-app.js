/*
 Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
 This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
 The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
 The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
 Code distributed by Google as part of the polymer project is also
 subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
 */
(function(document) {
  'use strict';

  Polymer({
    is: 'index-app',

    properties: {
      baseUrl: {
        type: String,
        value: ''
      },

      greeting: {
        type: String,
        value: 'Welcome!',
        notify: true
      }
    },

    attached: function () {
      page('*', function(ctx, next) {
        //app.scrollPageToTop();
        //app.closeDrawer();
        next();
      }.bind(this));

      page('/', function() {
        this.route = 'home';
      }.bind(this));

      page('', function() {
        this.route = 'home';
      }.bind(this));

      page('/origen', function() {
        this.route = 'origen';
      }.bind(this));

      // 404
      page('*', function() {
        this.$.toast.text = 'Can\'t find: ' + window.location.href  + '. Redirected you to Home Page';
        this.$.toast.show();
        page.redirect(this.baseUrl);
      }.bind(this));

      // add #! before urls
      page({
        hashbang: true
      });

      // Sets app default base URL
      this.baseUrl = '/';
      if (window.location.port === '') {  // if production
        // Uncomment app.baseURL below and
        // set app.baseURL to '/your-pathname/' if running from folder in production
        // app.baseUrl = '/polymer-starter-kit/';
      }

      this.displayInstalledToast = function () {
        // Check to make sure caching is actually enabled—it won't be in the dev environment.
        if (!Polymer.dom(document).querySelector('platinum-sw-cache').disabled) {
          Polymer.dom(document).querySelector('#caching-complete').show();
        }
      };

      // Listen for template bound event to know when bindings
      // have resolved and content has been stamped to the page
      this.addEventListener('dom-change', function () {
        console.log('Our app is ready to rock!');
      });

      // See https://github.com/Polymer/polymer/issues/1381
      window.addEventListener('WebComponentsReady', function () {
        // imports are loaded and elements have been registered
      });

      // Main area's paper-scroll-header-panel custom condensing transformation of
      // the appName in the middle-container and the bottom title in the bottom-container.
      // The appName is moved to top and shrunk on condensing. The bottom sub title
      // is shrunk to nothing on condensing.
      window.addEventListener('paper-header-transform', function (e) {
        var appName = this.$.mainToolbar.querySelector('.app-name');
        var middleContainer = this.$.mainToolbar.querySelector('.middle-container');
        var bottomContainer = this.$.mainToolbar.querySelector('.bottom-container');
        var detail = e.detail;
        var heightDiff = detail.height - detail.condensedHeight;
        var yRatio = Math.min(1, detail.y / heightDiff);
        // appName max size when condensed. The smaller the number the smaller the condensed size.
        var maxMiddleScale = 0.50;
        var auxHeight = heightDiff - detail.y;
        var auxScale = heightDiff / (1 - maxMiddleScale);
        var scaleMiddle = Math.max(maxMiddleScale,
            auxHeight / auxScale + maxMiddleScale);
        var scaleBottom = 1 - yRatio;

        // Move/translate middleContainer
        Polymer.Base.transform('translate3d(0,' + yRatio * 100 + '%,0)',
            middleContainer);

        // Scale bottomContainer and bottom sub title to nothing and back
        Polymer.Base.transform('scale(' + scaleBottom + ') translateZ(0)',
            bottomContainer);

        // Scale middleContainer appName
        Polymer.Base.transform('scale(' + scaleMiddle + ') translateZ(0)',
            appName);
      }.bind(this));

      // Scroll page to top and expand header
      this.scrollPageToTop = function () {
        this.$.headerPanelMain.scrollToTop(true);
      };

      this.closeDrawer = function () {
        this.$.paperDrawerPanel.closeDrawer();
      };
    }
  });
})(document);
