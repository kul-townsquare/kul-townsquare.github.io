<template>
  <Modal
    class="characters"
    @close="toggleModal('reference')"
    v-if="modals.reference && roles.size"
  >
    <font-awesome-icon
      @click="toggleModal('nightOrder')"
      icon="cloud-moon"
      class="toggle"
      title="Show Night Order"
    />
    <h3>
      角色能力表
      <font-awesome-icon icon="address-card" />
      {{ edition.name || "Custom Script" }}
    </h3>
    <div
      v-for="(teamRoles, team) in rolesGrouped"
      :key="team"
      :class="['team', team]"
    >
      <aside>
        <h4>{{ renameTeamName(team) }}</h4>
      </aside>
      <ul class="reference-list">
        <li v-for="role in teamRoles" :class="[team]" :key="role.id">
          <span
            class="icon"
            v-if="role.id"
            :style="{
              backgroundImage: `url(${
                role.image && grimoire.isImageOptIn
                  ? role.image
                  : require(
                      '../../assets/icons/' +
                        (role.imageAlt || role.id) +
                        '.png',
                    )
              })`,
            }"
          ></span>
          <div class="role">
            <!--            <span class="player" v-if="Object.keys(playersByRole).length">{{-->
            <!--              playersByRole[role.id] ? playersByRole[role.id].join(", ") : ""-->
            <!--            }}</span>-->
            <span class="name">{{ role.name }}</span>
            <span class="ability">{{ role.ability }}</span>
          </div>
        </li>
        <li :class="[team]"></li>
        <li :class="[team]"></li>
      </ul>
    </div>

    <div class="team jinxed" v-if="jinxed.length">
      <aside>
        <h4>Jinxed</h4>
      </aside>
      <ul>
        <li v-for="(jinx, index) in jinxed" :key="index">
          <span
            class="icon"
            :style="{
              backgroundImage: `url(${require(
                '../../assets/icons/' + jinx.first.id + '.png',
              )})`,
            }"
          ></span>
          <span
            class="icon"
            :style="{
              backgroundImage: `url(${require(
                '../../assets/icons/' + jinx.second.id + '.png',
              )})`,
            }"
          ></span>
          <div class="role">
            <span class="name"
              >{{ jinx.first.name }} & {{ jinx.second.name }}</span
            >
            <span class="ability">{{ jinx.reason }}</span>
          </div>
        </li>
        <li></li>
        <li></li>
      </ul>
    </div>
  </Modal>
</template>

<script>
import Modal from "./Modal";
import { mapMutations, mapState } from "vuex";

export default {
  components: {
    Modal,
  },
  computed: {
    /**
     * Return a list of jinxes in the form of role IDs and a reason
     * @returns {*[]} [{first, second, reason}]
     */
    jinxed: function () {
      const jinxed = [];
      this.roles.forEach((role) => {
        if (this.jinxes.get(role.id)) {
          this.jinxes.get(role.id).forEach((reason, second) => {
            if (this.roles.get(second)) {
              jinxed.push({
                first: role,
                second: this.roles.get(second),
                reason,
              });
            }
          });
        }
      });
      return jinxed;
    },
    rolesGrouped: function () {
      const rolesGrouped = {};
      this.roles.forEach((role) => {
        if (!rolesGrouped[role.team]) {
          rolesGrouped[role.team] = [];
        }
        rolesGrouped[role.team].push(role);
      });
      delete rolesGrouped["traveler"];
      // delete rolesGrouped["fabled"];
      return rolesGrouped;
    },
    playersByRole: function () {
      const players = {};
      this.players.forEach(({ name, role }) => {
        if (role && role.id && role.team !== "traveler") {
          if (!players[role.id]) {
            players[role.id] = [];
          }
          players[role.id].push(name);
        }
      });
      return players;
    },
    ...mapState(["roles", "modals", "edition", "grimoire", "jinxes"]),
    ...mapState("players", ["players"]),
  },
  methods: {
    renameTeamName(team) {
      switch (team) {
        case "townsfolk":
          return "镇民";
        case "outsider":
          return "外来者";
        case "minion":
          return "爪牙";
        case "fabled":
          return "传奇角色";
        case "demon":
          return "恶魔";
      }
      return team;
    },
    ...mapMutations(["toggleModal"]),
  },
};
</script>

<style lang="scss" scoped>
@import "../../vars.scss";

.toggle {
  position: absolute;
  left: 20px;
  top: 15px;
  cursor: pointer;
  &:hover {
    color: red;
  }
}

h3 {
  margin: 0 40px;
  svg {
    vertical-align: middle;
  }
}

.townsfolk {
  .name {
    color: $townsfolk;
  }
  aside {
    background: linear-gradient(-90deg, $townsfolk, transparent);
  }
}
.outsider {
  .name {
    color: $outsider;
  }
  aside {
    background: linear-gradient(-90deg, $outsider, transparent);
  }
}
.minion {
  .name {
    color: $minion;
  }
  aside {
    background: linear-gradient(-90deg, $minion, transparent);
  }
}
.demon {
  .name {
    color: $demon;
  }
  aside {
    background: linear-gradient(-90deg, $demon, transparent);
  }
}

.jinxed {
  .name {
    color: $fabled;
  }
  aside {
    background: linear-gradient(-90deg, $fabled, transparent);
  }
}

.fabled {
  .name {
    color: $fabled;
  }
  aside {
    background: linear-gradient(-90deg, $fabled, transparent);
  }
}

.team {
  display: flex;
  align-items: stretch;
  width: 100%;
  &:not(:last-child):after {
    content: " ";
    display: block;
    width: 25%;
    height: 1px;
    background: linear-gradient(90deg, #ffffffaa, transparent);
    position: absolute;
    left: 0;
    bottom: 0;
  }
  aside {
    width: 30px;
    display: flex;
    flex-grow: 0;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    align-content: center;
    overflow: hidden;
    text-shadow: 0 0 4px black;
  }

  h4 {
    //text-transform: uppercase;
    text-align: center;
    //transform: rotate(90deg);
    transform-origin: center;
    font-size: 18px;

    padding-top: min(10px);
    padding-bottom: min(10px);

    writing-mode: vertical-rl;
    text-orientation: upright;
  }

  &.jinxed {
    .icon {
      margin: 0 -5px;
    }
  }
}

ul {
  flex-grow: 1;
  display: flex;
  padding: 5px 0;

  li {
    display: flex;
    align-items: center;
    flex-grow: 1;
    width: min(100%, 300px);
    .icon {
      width: 8vh;
      background-size: cover;
      background-position: 0 -5px;
      flex-shrink: 0;
      flex-grow: 0;
      &:after {
        content: " ";
        display: block;
        padding-top: 75%;
      }
    }
    .role {
      line-height: 1.1rem;
      flex-grow: 1;
    }
    .name {
      font-weight: bold;
      font-size: 0.9rem;
      display: block;
    }
    .player {
      color: #888;
      float: right;
      font-size: 0.9rem;
    }
    .ability {
      font-size: 0.9rem;
    }
  }
}

/** break into 1 column below 980px **/
@media screen and (max-width: 980px) {
  .modal {
    max-width: 60%;
  }
  ul {
    li {
      .icon {
        width: 6vh;
      }
      .role {
        line-height: 1.1rem;
      }
      .name {
        font-size: 0.85rem;
      }
      .player {
        font-size: 0.85rem;
      }
      .ability {
        font-size: 0.85rem;
      }
    }
  }
}

/** trim icon size on maximized one-column sheet **/
@media screen and (max-width: 991.98px) {
  .characters .modal.maximized ul li .icon {
    width: 5.1vh;
  }
}

/** hide players when town square is set to "public" **/
#townsquare.public ~ .characters .modal .player {
  display: none;
}

.reference-list {
  align-content: normal !important;
  align-items: normal !important;
}
</style>
