<template>
  <v-icon
    :class="`${active ? 'active' : ''}`"
    class="dir-icon"
    @click="active = true"
  >{{ icon }}</v-icon>
</template>

<script>

export default {
  props: {
    direction: String,
  },
  data: () => ({
    active: false
  }),
  computed: {
    icon() {
      let icon = '';
      switch (this.direction) {
        case 'stop':
          icon = 'mdi-octagon';
          break;
        case 'forwards':
          icon = 'mdi-fast-forward';
          break;
        case 'backwards':
          icon = 'mdi-rewind';
          break;
      }

      return icon;
    }
  }
}

</script>

<style>
  .v-icon.dir-icon {
    font-size: 300px;
  }

  .v-icon.dir-icon:hover {
    cursor: pointer;
  }
</style>
