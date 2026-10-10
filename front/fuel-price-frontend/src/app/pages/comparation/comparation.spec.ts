import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Comparation } from './comparation';

describe('Comparation', () => {
  let component: Comparation;
  let fixture: ComponentFixture<Comparation>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Comparation],
    }).compileComponents();

    fixture = TestBed.createComponent(Comparation);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
