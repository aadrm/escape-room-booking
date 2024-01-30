<script lang="ts">
import { defineComponent } from "vue";
import SlotsCalendar from "../components/SlotsCalendar.vue";

export default defineComponent({
  components: {
    SlotsCalendar,
  },
});
</script>

<template>
  <main>
    <SlotsCalendar />
  </main>
</template>

<style scoped>
.has-slots {
  color: lightgreen;
}
</style>
