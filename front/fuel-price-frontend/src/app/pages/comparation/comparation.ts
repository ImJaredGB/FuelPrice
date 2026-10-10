
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { FuelService } from '../../core/services/fuel';
import { FuelType } from '../../core/models/fuel-type';
import { ProvinceComparation } from '../../core/models/province-comparation';
import { ProvinceComparationComponent } from '../../components/province-comparation';

@Component({
  selector: 'app-comparation',
  imports: [FormsModule, ProvinceComparationComponent],
  templateUrl: './comparation.html',
  styleUrl: './comparation.css',
})
export class Comparation implements OnInit {

  fuelTypes: FuelType[] = [];
  selectedFuel = '';

  provinces: ProvinceComparation[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private fuelService: FuelService,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {

    this.fuelService.getFuelTypes().subscribe({
      next: (data) => {
        this.fuelTypes = data;

        if (this.fuelTypes.length > 0) {
          this.selectedFuel = this.fuelTypes[0].code;
          this.loadComparation();
        }

        this.changeDetectorRef.detectChanges();
      },
      error: (error) => {
        console.error('Error loading fuel types:', error);
        this.errorMessage = 'No se pudieron cargar los combustibles.';
        this.changeDetectorRef.detectChanges();
      }
    });
  }

  loadComparation(): void {

    if (!this.selectedFuel) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.fuelService.getProvinceComparation(
      this.selectedFuel
    ).subscribe({
      next: (data) => {
        this.provinces = data;
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      },
      error: (error) => {
        console.error('Error loading Comparation:', error);
        this.errorMessage = 'No se pudo cargar la comparativa.';
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      }
    });
  }

  onFuelChange(): void {
    this.loadComparation();
  }
}
