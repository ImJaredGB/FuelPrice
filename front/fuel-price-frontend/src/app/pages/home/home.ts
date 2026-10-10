import { Component } from '@angular/core';
import { FuelUpdateControlComponent } from '../../components/fuel-update-control';

@Component({
  selector: 'app-home',
  imports: [FuelUpdateControlComponent],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {}
