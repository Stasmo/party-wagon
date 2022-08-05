<template>
  <v-app>
    <v-app-bar
      app
      color="purple"
      dark
    >
    </v-app-bar>

    <v-main>
      <v-card>
        <v-card-title primary-title>
          Party Wagon Control
        </v-card-title>
        <v-card-text>
          <v-text-field
            name="name"
            label="Message"
            id="id"
            v-model="message"
            v-on:keyup.enter="sendMessage"
          ></v-text-field>
          <v-divider></v-divider>
          <v-btn class="ma-4 black--text" color="yellow" @click="scan">Pair</v-btn>
          <v-divider></v-divider>
          <v-card>
            <v-btn-toggle mandatory v-model="direction">
              <v-btn
                v-for="btn in directionButtons"
                :key="btn.dir"
                style="height: 30vw;"
              >
                <v-icon
                  style="font-size: 30vw;"
                >{{ btn.icon }}</v-icon>
              </v-btn>
            </v-btn-toggle>
          </v-card>
        </v-card-text>
      </v-card>
    </v-main>
  </v-app>
</template>

<script>

const DIRECTION_FORWARDS = 'f';
const DIRECTION_BACKWARDS = 'b';
const DIRECTION_STOP = 's';

// import DirectionButton from './components/DirectionButton'
import PartyWagon from './wagon'
export default {
  name: 'App',

  components: {
    // DirectionButton
  },

  data: () => ({
    device: null,
    direction: 1,
    message: '',
    directionButtons: [
      { dir: DIRECTION_BACKWARDS, icon: 'mdi-rewind' },
      { dir: DIRECTION_STOP, icon: 'mdi-octagon'},
      { dir: DIRECTION_FORWARDS, icon: 'mdi-fast-forward' },
    ]
  }),

  created() {
    this.device = new PartyWagon();
  },
  watch: {
    direction() {
      const dir = this.directionButtons[this.direction].dir;
      if (this.device.connected) {
        this.device.setDirection(dir);
      }
    }
  },

  methods: {
    async scan() {
      await this.device.request();
      this.device.connect();
    },
    sendMessage() {
      this.device.writeLine(this.message);
      this.message = "";
    }
  }
};
</script>
