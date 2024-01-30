<script lang="ts">
import axios from "axios";
import { defineComponent } from "vue";
import CalendarDay from "./CalendarDay.vue";
import { dateToISOYearMonthDayString } from "@/utils/dateHelpers";

export default defineComponent({
  components: {
    CalendarDay,
  },
  data() {
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1; // months are zero-indexed
    return {
      daysOfWeek: this.getDaysOfWeek(),
      currentDate,
      currentMonth,
      currentYear,
      slots: null as any,
    };
  },
  props: {
    month: {
      type: Number,
      required: true,
    },
    year: {
      type: Number,
      required: true,
    },
  },
  computed: {
    monthName(): String {
      const options = { month: "long" };
      const locale = navigator.language || "de";
      const date = new Date(this.currentYear, this.currentMonth - 1, 1);
      return date.toLocaleDateString(locale, options);
    },
    calendar() {
      try {
        const year = this.currentYear;
        const month = this.currentMonth;
        const firstDayOfMonth = new Date(year, month - 1, 1);
        const lastDayOfMonth = new Date(year, month, 0);
        const daysInMonth = lastDayOfMonth.getDate();
        const firstDayOfWeek = firstDayOfMonth.getDay() - 1; // -1 makes to consider Monday as the first day of a week
        let calendar = [[]];
        let currentWeek = calendar[0];
        for (let i = 0; i < firstDayOfWeek; i++) {
          currentWeek.push({});
        }
        for (let day = 1; day <= daysInMonth; day++) {
          const date = new Date(year, month - 1, day);
          const ISODate = dateToISOYearMonthDayString(date);
          const hasSlots = this.checkIfDayHasSlots(ISODate);
          currentWeek.push({ day, month, year, hasSlots });
          if (currentWeek.length === 7 && day < daysInMonth) {
            currentWeek = [];
            calendar.push(currentWeek);
          }
        }
        return calendar;
      } catch (error) {
        return [[]];
      }
    },
  },
  methods: {
    getDaysOfWeek() {
      const options = { weekday: "short" };
      const locale = navigator.language || "de";
      const dayNames = Array.from({ length: 7 }, (_, index) => {
        const date = new Date(2024, 0, index + 1); // 1 January 2024 (a Monday)
        return date.toLocaleDateString(locale, options);
      });
      return dayNames;
    },
    prevMonth() {
      this.currentMonth -= 1;
      if (this.currentMonth < 1) {
        this.currentMonth = 12;
        this.currentYear -= 1;
      }
      this.fetchSlots();
    },
    nextMonth() {
      this.currentMonth += 1;
      if (this.currentMonth > 12) {
        this.currentMonth = 1;
        this.currentYear += 1;
      }
      this.fetchSlots();
    },
    async fetchSlots() {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/slots/days_available/${this.currentYear}/${this.currentMonth}`
        );
        this.slots = response.data;
      } catch (error) {
        console.error("Error fetching slots:", error);
      }
    },
    checkIfDayHasSlots(ISODate: String): boolean {
      if (this.slots) {
        const slotsString = JSON.stringify(this.slots);
        const included = slotsString.includes(ISODate);
        return included;
      }
    },
  },
  mounted: function () {
    this.fetchSlots();
  },
});
</script>

<template>
  <h2>{{ monthName }} {{ currentYear }}</h2>
  <div>
    <button @click="prevMonth">Previous</button>
    <button @click="nextMonth">Next</button>
  </div>
  <table>
    <thead>
      <tr>
        <th v-for="day in daysOfWeek" :key="day">{{ day }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="week in calendar" :key="week[0].day">
        <CalendarDay
          v-for="day in week"
          :key="day.day"
          :day="day"
          @select-date="selectDate"
        />
      </tr>
    </tbody>
  </table>
  <div v-if="slots">
    <pre>{{ slots }}</pre>
  </div>
</template>
