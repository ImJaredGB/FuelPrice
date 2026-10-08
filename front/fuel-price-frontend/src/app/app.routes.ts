import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/home/home').then(
        m => m.Home
      )
  },
  {
    path: 'stations',
    loadComponent: () =>
      import('./pages/stations/stations').then(
        m => m.Stations
      )
  },
  {
    path: '**',
    loadComponent: () =>
      import('./pages/error/error').then(
        m => m.Error
      )
  }
];