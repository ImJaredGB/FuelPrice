import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Station } from '../models/station';
import { Province } from '../models/province';
import { Municipality } from '../models/municipality';
import { FuelType } from '../models/fuel-type';

@Injectable({
  providedIn: 'root'
})
export class FuelService {

  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getProvinces(): Observable<Province[]> {
    return this.http.get<Province[]>(
      `${this.apiUrl}/provinces/`
    );
  }

  getMunicipalities(): Observable<Municipality[]> {
    return this.http.get<Municipality[]>(
      `${this.apiUrl}/municipalities/`
    );
  }

  getFuelTypes(): Observable<FuelType[]> {
    return this.http.get<FuelType[]>(
      `${this.apiUrl}/fuel-types/`
    );
  }

  getStations(
    province?: string,
    municipality?: string,
    fuel?: string
  ): Observable<Station[]> {

    let params = new HttpParams();

    if (province) {
      params = params.set('province', province);
    }

    if (municipality) {
      params = params.set('municipality', municipality);
    }

    if (fuel) {
      params = params.set('fuel', fuel);
    }

    return this.http.get<Station[]>(
      `${this.apiUrl}/stations/`,
      { params }
    );
  }
}