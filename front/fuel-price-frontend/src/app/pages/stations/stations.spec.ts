import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Stations } from './stations';

describe('Stations', () => {
  let component: Stations;
  let fixture: ComponentFixture<Stations>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Stations],
    }).compileComponents();

    fixture = TestBed.createComponent(Stations);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
