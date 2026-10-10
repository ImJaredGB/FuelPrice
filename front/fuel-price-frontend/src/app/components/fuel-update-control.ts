
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FuelUpdateService,
  FuelUpdateConfig
} from '../core/services/fuel-update';

@Component({
  selector: 'app-fuel-update-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fuel-update-control.html'
})
export class FuelUpdateControlComponent implements OnInit {
  enabled = false;
  loading = true;
  saving = false;
  errorMessage = '';
  message = '';

  constructor(private fuelUpdateService: FuelUpdateService) {}

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig(): void {
    this.loading = true;
    this.errorMessage = '';

    this.fuelUpdateService.getConfig().subscribe({
      next: (config: FuelUpdateConfig) => {
        this.enabled = config.enabled;
        this.loading = false;
      },
      error: () => {
        this.errorMessage =
          'No se pudo consultar la configuración. Comprueba tu sesión de administrador.';
        this.loading = false;
      }
    });
  }

  toggleUpdate(): void {
    if (this.loading || this.saving) {
      return;
    }

    const newValue = !this.enabled;

    this.saving = true;
    this.errorMessage = '';
    this.message = '';

    this.fuelUpdateService.setEnabled(newValue).subscribe({
      next: (config: FuelUpdateConfig) => {
        this.enabled = config.enabled;
        this.message = config.message ?? 'Configuración actualizada.';
        this.saving = false;
      },
      error: () => {
        this.errorMessage =
          'No se pudo guardar el cambio. Comprueba la sesión, los permisos y CSRF.';
        this.saving = false;
      }
    });
  }
}
