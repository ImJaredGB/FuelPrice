import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { FuelService } from '../../core/services/fuel';

import { Station } from '../../core/models/station';
import { Province } from '../../core/models/province';
import { Municipality } from '../../core/models/municipality';
import { FuelType } from '../../core/models/fuel-type';

@Component({
  selector: 'app-stations',
  imports: [FormsModule],
  templateUrl: './stations.html',
  styleUrl: './stations.css'
})
export class Stations implements OnInit {

  provinces: Province[] = [];
  municipalities: Municipality[] = [];
  fuelTypes: FuelType[] = [];

  filteredMunicipalities: Municipality[] = [];

  stations: Station[] = [];

  selectedProvince = '';
  selectedMunicipality = '';
  selectedFuel = '';

  loading = false;

  constructor(
    private fuelService: FuelService,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

    this.fuelService.getProvinces().subscribe({
      next: (data) => {
        this.provinces = data;
      },
      error: (error) => {
        console.error('Error loading provinces:', error);
      }
    });

    this.fuelService.getMunicipalities().subscribe({
      next: (data) => {
        this.municipalities = data;
      },
      error: (error) => {
        console.error('Error loading municipalities:', error);
      }
    });

    this.fuelService.getFuelTypes().subscribe({
      next: (data) => {
        this.fuelTypes = data;
      },
      error: (error) => {
        console.error('Error loading fuel types:', error);
      }
    });
  }

  onProvinceChange(): void {

    this.selectedMunicipality = '';

    if (!this.selectedProvince) {
      this.filteredMunicipalities = [];
      return;
    }

    const province = this.provinces.find(
      province => province.api_id === this.selectedProvince
    );

    if (!province) {
      this.filteredMunicipalities = [];
      return;
    }

    this.filteredMunicipalities = this.municipalities.filter(
      municipality =>
        municipality.province === province.id
    );
  }

  searchStations(): void {

    this.loading = true;

    this.fuelService.getStations(
      this.selectedProvince,
      this.selectedMunicipality,
      this.selectedFuel
    ).subscribe({
      next: (data) => {

        console.log('Stations received:', data);

        this.stations = data;
        this.loading = false;

        this.changeDetectorRef.detectChanges();
      },

      error: (error) => {

        console.error('Error loading stations:', error);

        this.loading = false;

        this.changeDetectorRef.detectChanges();
      }
    });
  }
}