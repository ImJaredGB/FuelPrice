
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FuelUpdateConfig {
  enabled: boolean;
  updated_at: string;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class FuelUpdateService {
  private readonly apiUrl =
    'http://localhost:8000/api/fuel/update-config/';

  constructor(private http: HttpClient) {}

  getConfig(): Observable<FuelUpdateConfig> {
    return this.http.get<FuelUpdateConfig>(
      this.apiUrl,
      { withCredentials: true }
    );
  }

  setEnabled(enabled: boolean): Observable<FuelUpdateConfig> {
    const csrfToken = this.getCookie('csrftoken');

    const headers = csrfToken
      ? new HttpHeaders({ 'X-CSRFToken': csrfToken })
      : new HttpHeaders();

    return this.http.post<FuelUpdateConfig>(
      this.apiUrl,
      { enabled },
      {
        headers,
        withCredentials: true
      }
    );
  }

  private getCookie(name: string): string | null {
    const prefix = `${name}=`;

    const cookie = document.cookie
      .split('; ')
      .find(item => item.startsWith(prefix));

    return cookie
      ? decodeURIComponent(cookie.substring(prefix.length))
      : null;
  }
}
