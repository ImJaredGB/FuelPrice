import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { FuelService } from '../core/services/fuel';
import { ProvinceComparation } from '../core/models/province-comparation';

interface FuelOption {
  code: string;
  name: string;
}

@Component({
  selector: 'app-province-comparation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './province-comparation.html',
})
export class ProvinceComparationComponent implements OnInit {
  fuelTypes: FuelOption[] = [];
  selectedFuelCode = '';
  provinces: ProvinceComparation[] = [];

  loading = false;
  errorMessage = '';

  constructor(
    private fuelService: FuelService,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.fuelService.getFuelTypes().subscribe({
      next: (fuelTypes: FuelOption[]) => {
        this.fuelTypes = fuelTypes;

        if (fuelTypes.length > 0) {
          this.selectedFuelCode = fuelTypes[0].code;
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

  onFuelChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.selectedFuelCode = select.value;
    this.loadComparation();
  }

  loadComparation(): void {
    if (!this.selectedFuelCode) {
      this.loading = false;
      this.changeDetectorRef.detectChanges();
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.changeDetectorRef.detectChanges();

    this.fuelService
      .getProvinceComparation(this.selectedFuelCode)
      .subscribe({
        next: (provinces) => {
          this.provinces = provinces;
          this.loading = false;

          this.changeDetectorRef.detectChanges();
        },
        error: (error) => {
          console.error('Error loading comparison:', error);

          this.errorMessage = 'No se pudo cargar la comparativa.';
          this.loading = false;

          this.changeDetectorRef.detectChanges();
        }
      });
  }
}