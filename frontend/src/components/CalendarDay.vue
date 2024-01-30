<script lang="ts">
export default {
  props: {
    day: {
      type: Object,
      required: true,
    },
  },
  methods: {
    selectDate(day) {
      console.log(day.day, day.month, day.year);
    },
    handleClick() {
      if (this.day.hasSlots) {
        this.$emit("select-date", this.day);
      }
    },
  },
};
</script>

<template>
  <td @click="day.hasSlots && selectDate(day)" :class="{ 'has-slots': day.hasSlots }">
    {{ day.day }}
    {{ day.month }}
    {{ day.year }}
    {{ day.hasSlots }}
    <!-- Render slot information here -->
    <!-- Example: {{ slots }} -->
  </td>
</template>

<style scoped>
.has-slots {
  color: lightgreen;
}
</style>
