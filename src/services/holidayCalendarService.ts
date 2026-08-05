import { api } from '../lib/api';

export interface HolidayDate {
  _id?: string;
  calendarId: string;
  holidayDate: string; // YYYY-MM-DD
  holidayName: string;
  holidayType: string; // Mandatory, Restricted, Optional, Branch, Festival, National
  isRecurring?: boolean;
  remarks?: string;
  status?: string;
}

export interface HolidayCalendar {
  _id?: string;
  name: string;
  description?: string;
  year: number;
  branchId?: string;
  branchName?: string;
  branchCode?: string;
  effectiveFrom?: string;
  effectiveTo?: string;
  status?: string;
  holidayCount?: number;
}

export async function getHolidayCalendars(): Promise<HolidayCalendar[]> {
  const res = await api.get<any>('/v2/holiday/holiday-calendar/');
  return res?.data || res || [];
}

export async function createHolidayCalendar(calendar: HolidayCalendar) {
  return api.post<HolidayCalendar>('/v2/holiday/holiday-calendar/', calendar);
}

export async function updateHolidayCalendar(id: string, calendar: HolidayCalendar) {
  return api.put<HolidayCalendar>(`/v2/holiday/holiday-calendar/${id}`, calendar);
}

export async function deleteHolidayCalendar(id: string) {
  return api.delete(`/v2/holiday/holiday-calendar/${id}`);
}

export async function getHolidayDates(calendarId: string) {
  return api.get<HolidayDate[]>(`/v2/holiday/holiday-calendar/${calendarId}/dates`);
}

export async function createHolidayDate(calendarId: string, date: HolidayDate) {
  return api.post<HolidayDate>(`/v2/holiday/holiday-calendar/${calendarId}/dates`, date);
}

export async function updateHolidayDate(calendarId: string, dateId: string, date: HolidayDate) {
  return api.put<HolidayDate>(`/v2/holiday/holiday-calendar/${calendarId}/dates/${dateId}`, date);
}

export async function deleteHolidayDate(calendarId: string, dateId: string) {
  return api.delete(`/v2/holiday/holiday-calendar/${calendarId}/dates/${dateId}`);
}
