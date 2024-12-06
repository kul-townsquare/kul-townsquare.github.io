<template>
  <Modal v-if="modals.role && availableRoles.length" @close="close">
    <h3>
     为
      {{
        playerIndex >= 0 && players.length
          ? players[playerIndex].name
          : "恶魔的伪装"
      }}
      选择角色
    </h3>
    <ul class="tokens" v-if="tab === 'editionRoles' || !otherTravelers.size">
      <li
        v-for="role in availableRoles"
        :class="[role.team]"
        :key="role.id"
        @click="setRole(role)"
      >
        <Token :role="role" />
      </li>
    </ul>
    <ul class="tokens" v-if="tab === 'otherTravelers' && otherTravelers.size">
      <li
        v-for="role in otherTravelers.values()"
        :class="[role.team]"
        :key="role.id"
        @click="setRole(role)"
      >
        <Token :role="role" />
      </li>
    </ul>
    <div
      class="button-group"
      v-if="playerIndex >= 0 && otherTravelers.size && !session.isSpectator"
    >
      <span
        class="button"
        :class="{ townsfolk: tab === 'editionRoles' }"
        @click="tab = 'editionRoles'"
        >剧本角色</span
      >
      <span
        class="button"
        :class="{ townsfolk: tab === 'otherTravelers' }"
        @click="tab = 'otherTravelers'"
        >旅行者</span
      >
    </div>
  </Modal>
</template>

<script>
import { mapMutations, mapState } from "vuex";
import Modal from "./Modal";
import Token from "../Token";

export default {
  components: { Token, Modal },
  props: ["playerIndex"],
  computed: {
    availableRoles() {
      const availableRoles = [];
      const players = this.$store.state.players.players;
      this.$store.state.roles.forEach((role) => {
        // don't show bluff roles that are already assigned to players
        if (
          this.playerIndex >= 0 ||
          (this.playerIndex < 0 &&
            !players.some((player) => player.role.id === role.id))
        ) {
          availableRoles.push(role);
        }
      });
      availableRoles.push({});
      return availableRoles;
    },
    ...mapState(["modals", "roles", "session"]),
    ...mapState("players", ["players"]),
    ...mapState(["otherTravelers"]),
  },
  data() {
    return {
      tab: "editionRoles",
    };
  },
  methods: {
    setRole(role) {
      if (this.playerIndex < 0) {
        // assign to bluff slot (index < 0)
        this.$store.commit("players/setBluff", {
          index: this.playerIndex * -1 - 1,
          role,
        });
      } else {
        if (this.session.isSpectator && role.team === "traveler") return;
        // assign to player
        const player = this.$store.state.players.players[this.playerIndex];
        this.$store.commit("players/update", {
          player,
          property: "role",
          value: role,
        });
      }
      this.tab = "editionRoles";
      this.$store.commit("toggleModal", "role");
    },
    close() {
      this.tab = "editionRoles";
      this.toggleModal("role");
    },
    ...mapMutations(["toggleModal"]),
  },
};
</script>

<style scoped lang="scss">
@import "../../vars.scss";

ul.tokens li {
  border-radius: 50%;
  width: max(6vw, 60px);
  margin: 1%;
  transition: transform 500ms ease;

  &.townsfolk {
    box-shadow:
      0 0 10px $townsfolk,
      0 0 10px #004cff;
  }
  &.outsider {
    box-shadow:
      0 0 10px $outsider,
      0 0 10px $outsider;
  }
  &.minion {
    box-shadow:
      0 0 10px $minion,
      0 0 10px $minion;
  }
  &.demon {
    box-shadow:
      0 0 10px $demon,
      0 0 10px $demon;
  }
  &.traveler {
    box-shadow:
      0 0 10px $traveler,
      0 0 10px $traveler;
  }
  &:hover {
    transform: scale(1.2);
    z-index: 10;
  }
}

#townsquare.spectator ul.tokens li.traveler {
  display: none;
}
</style>
