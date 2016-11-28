'use strict';

/**
 * @ngdoc overview
 * @name pvcApp
 * @description
 * # pvcApp
 *
 * Main module of the application.
 */
angular
  .module('pvcApp', [
    'ngResource',
    'ui.router'
  ])
  .config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
    .state({
        name: 'app',
        url: '/app',
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
    })
    .state({
        name: 'about',
        url: '/about',
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
    })
    .state({
        name: 'contact',
        url: '/contact',
        template: '<p>This is the contact view.</p>'
    })
    .state({
        name: 'userSite',
        url: '/userSite',
        templateUrl: 'views/usersite.html',
        controller: 'UsersiteCtrl'
    });
    
    $urlRouterProvider.otherwise('/userSite');
    
  });
