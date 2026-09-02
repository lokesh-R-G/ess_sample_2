import { api } from '../lib/api';

export interface HolidayDate {
  id?: string;
  _id?: string;
  holidayCode?: string;
  calendarId?: string;
  holidayDate: string; // YYYY-MM-DD
  holidayName: string;
  holidayType: string; // Mandatory, Restricted, Optional, Branch, Festival, National
  isRecurring?: boolean;
  remarks?: string;
  status?: string;
  version?: number;
  isCurrent?: boolean;
}

export interface HolidayCalendar {
  id?: string;
  _id?: string;
  holidayCalendarCode?: string;
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
  version?: number;
  isCurrent?: boolean;
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
  const { calendarId: _, id, _id, ...payload } = date;
  return api.post<HolidayDate>(`/v2/holiday/holiday-calendar/${calendarId}/dates`, payload);
}

export async function updateHolidayDate(calendarId: string, dateId: string, date: HolidayDate) {
  const { calendarId: _, id, _id, ...payload } = date;
  return api.put<HolidayDate>(`/v2/holiday/holiday-calendar/${calendarId}/dates/${dateId}`, payload);
}

export async function deleteHolidayDate(calendarId: string, dateId: string) {
  return api.delete(`/v2/holiday/holiday-calendar/${calendarId}/dates/${dateId}`);
}
