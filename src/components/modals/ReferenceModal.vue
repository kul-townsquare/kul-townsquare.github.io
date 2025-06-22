<!-- eslint-disable prettier/prettier -->
<template>
  <Modal class="characters" @close="toggleModal('reference')" v-if="modals.reference && roles.size">
    <font-awesome-icon @click="toggleModal('nightOrder')" icon="cloud-moon" class="toggle" title="Show Night Order" />
    <h3>
      角色能力表
      <font-awesome-icon icon="address-card" />
      {{ edition.name || "Custom Script" }}
    </h3>
    <div class="filter-tags">
      <div class="filter-row search-row">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索角色名称或能力描述..." 
          class="search-input"
          @focus="disableShortcuts"
          @blur="enableShortcuts"
        />
        <span class="tag clear-search" v-if="searchQuery" @click="clearSearch">
          <font-awesome-icon icon="times" />
          清除
        </span>
      </div>
      <div class="filter-row">
        <span class="tag filter-toggle" :class="{ active: showAdvancedFilters }"
          @click="showAdvancedFilters = !showAdvancedFilters">
          <font-awesome-icon :icon="showAdvancedFilters ? 'filter' : 'filter'" />
          {{ showAdvancedFilters ? '收起' : '筛选' }}
        </span>
        <span class="tag" :class="{ active: activeFilters.includes('all') }" @click="toggleFilter('all')">
          全部
        </span>
        <span class="tag townsfolk" :class="{ active: activeFilters.includes('townsfolk') }"
          @click="toggleFilter('townsfolk')">
          镇民
        </span>
        <span class="tag outsider" :class="{ active: activeFilters.includes('outsider') }"
          @click="toggleFilter('outsider')">
          外来者
        </span>
        <span class="tag minion" :class="{ active: activeFilters.includes('minion') }" @click="toggleFilter('minion')">
          爪牙
        </span>
        <span class="tag demon" :class="{ active: activeFilters.includes('demon') }" @click="toggleFilter('demon')">
          恶魔
        </span>
        <span class="tag fabled" :class="{ active: activeFilters.includes('fabled') }" @click="toggleFilter('fabled')"
          v-if="rolesGrouped.fabled && rolesGrouped.fabled.length">
          传奇角色
        </span>
      </div>
      <div class="filter-row" v-if="showAdvancedFilters">
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('firstNightInfo') }"
          @click="toggleFilter('firstNightInfo')">
          首个夜晚#你会得知
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('gainAbility') }"
          @click="toggleFilter('gainAbility')">
          获得能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightInfo') }"
          @click="toggleFilter('everyNightInfo')">
          每个夜晚#你会得知
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightChoose') }"
          @click="toggleFilter('everyNightChoose')">
          每个夜晚#你要选择
        </span>
      </div>
      <div class="filter-row" v-if="showAdvancedFilters">
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('limitedAbility') }"
          @click="toggleFilter('limitedAbility')">
          限次能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightChooseAny') }"
          @click="toggleFilter('everyNightChooseAny')">
          每个夜晚*#你要选择
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightInfoAny') }"
          @click="toggleFilter('everyNightInfoAny')">
          每个夜晚*#你会得知
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('passiveTrigger') }"
          @click="toggleFilter('passiveTrigger')">
          被动触发
        </span>
      </div>
      <div class="filter-row" v-if="showAdvancedFilters">
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('publicTrigger') }"
          @click="toggleFilter('publicTrigger')">
          公开触发能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('visitStoryteller') }"
          @click="toggleFilter('visitStoryteller')">
          拜访说书人
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('deathTrigger') }"
          @click="toggleFilter('deathTrigger')">
          死亡触发能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('specialWinLose') }"
          @click="toggleFilter('specialWinLose')">
          特殊胜利失败条件
        </span>
      </div>
      <div class="filter-row" v-if="showAdvancedFilters">
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('nomination') }"
          @click="toggleFilter('nomination')">
          提名
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('cognitiveOverride') }"
          @click="toggleFilter('cognitiveOverride')">
          认知覆盖
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('deathTriggerChoose') }"
          @click="toggleFilter('deathTriggerChoose')">
          死亡触发能力#你要选择
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('viewGrimoire') }"
          @click="toggleFilter('viewGrimoire')">
          查看魔典
        </span>
      </div>
      <div class="filter-row" v-if="showAdvancedFilters">
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('passiveTriggerAbility') }"
          @click="toggleFilter('passiveTriggerAbility')">
          被动触发能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightChooseRole') }"
          @click="toggleFilter('everyNightChooseRole')">
          每个夜晚*#你要选择角色
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('everyNightActivate') }"
          @click="toggleFilter('everyNightActivate')">
          每个夜晚*#你是否发动能力
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('settingsInteraction') }"
          @click="toggleFilter('settingsInteraction')">
          设置调整#互动干扰
        </span>
        <span class="tag ability-filter" :class="{ active: activeFilters.includes('exposeRole') }"
          @click="toggleFilter('exposeRole')">
          暴露角色
        </span>
      </div>
    </div>
    <div v-for="(teamRoles, team) in filteredRolesGrouped" :key="team" :class="['team', team]">
      <aside>
        <h4>{{ renameTeamName(team) }}</h4>
      </aside>
      <ul class="reference-list">
        <li v-for="role in teamRoles" :class="[team]" :key="role.id">
          <span class="icon" v-if="role.id" :style="{
            backgroundImage: `url(${role.image && grimoire.isImageOptIn
              ? role.image
              : require(
                '../../assets/icons/' +
                (role.imageAlt || role.id) +
                '.png',
              )
              })`,
          }"></span>
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
          <span class="icon" :style="{
            backgroundImage: `url(${require(
              '../../assets/icons/' + jinx.first.id + '.png',
            )})`,
          }"></span>
          <span class="icon" :style="{
            backgroundImage: `url(${require(
              '../../assets/icons/' + jinx.second.id + '.png',
            )})`,
          }"></span>
          <div class="role">
            <span class="name">{{ jinx.first.name }} & {{ jinx.second.name }}</span>
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
  data() {
    return {
      // 当前激活的筛选条件，默认显示"全部"
      activeFilters: ["all"],
      // 控制是否显示高级筛选选项
      showAdvancedFilters: false,
      // 搜索查询
      searchQuery: "",
      // 角色团队筛选条件列表
      teamFilters: [
        "all", // 全部角色
        "townsfolk", // 镇民
        "outsider", // 外来者
        "minion", // 爪牙
        "demon", // 恶魔
        "fabled", // 传奇角色
      ],
      // 角色能力筛选条件列表
      abilityFilters: [
        "firstNightInfo", // 首个夜晚获得信息
        "gainAbility", // 获得能力
        "everyNightInfo", // 每个夜晚获得信息
        "everyNightChoose", // 每个夜晚选择
        "limitedAbility", // 限次能力
        "everyNightChooseAny", // 每个夜晚*选择
        "everyNightInfoAny", // 每个夜晚*获得信息
        "passiveTrigger", // 被动触发
        "publicTrigger", // 公开触发能力
        "visitStoryteller", // 拜访说书人
        "deathTrigger", // 死亡触发能力
        "specialWinLose", // 特殊胜利失败条件
        "nomination", // 提名相关
        "cognitiveOverride", // 认知覆盖
        "deathTriggerChoose", // 死亡触发选择
        "viewGrimoire", // 查看魔典
        "passiveTriggerAbility", // 被动触发能力
        "everyNightChooseRole", // 每个夜晚选择角色
        "everyNightActivate", // 每个夜晚是否发动能力
        "settingsInteraction", // 设置调整互动干扰
        "exposeRole", // 暴露角色
      ],
    };
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
    filteredRolesGrouped: function () {
      // 如果只选择了"全部"，显示所有角色
      if (
        this.activeFilters.length === 1 &&
        this.activeFilters.includes("all")
      ) {
        return this.applySearch(this.rolesGrouped);
      }

      const filtered = {};

      // 获取激活的团队筛选和能力筛选
      const teamFiltersActive = this.activeFilters.filter((f) =>
        this.teamFilters.includes(f),
      );
      const abilityFiltersActive = this.activeFilters.filter((f) =>
        this.abilityFilters.includes(f),
      );

      Object.keys(this.rolesGrouped).forEach((team) => {
        let filteredRoles = this.rolesGrouped[team];

        // 应用团队筛选（始终使用OR逻辑）
        if (teamFiltersActive.length > 0 && !teamFiltersActive.includes(team)) {
          return; // 跳过不匹配的团队
        }

        // 如果展开高级筛选且有能力筛选，应用能力筛选（使用AND逻辑，即交集）
        if (this.showAdvancedFilters && abilityFiltersActive.length > 0) {
          filteredRoles = filteredRoles.filter((role) => {
            return abilityFiltersActive.every((filter) =>
              this.matchesAbilityFilter(role, filter),
            );
          });
        }

        if (filteredRoles.length > 0) {
          filtered[team] = filteredRoles;
        }
      });

      return this.applySearch(filtered);
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
    disableShortcuts() {
      this.$store.commit("setShortcutsDisabled", true);
    },
    enableShortcuts() {
      this.$store.commit("setShortcutsDisabled", false);
    },
    toggleFilter(filter) {
      if (filter === "all") {
        this.activeFilters = ["all"];
        return;
      }

      // 移除"全部"筛选
      this.activeFilters = this.activeFilters.filter((f) => f !== "all");

      // 切换筛选
      if (this.activeFilters.includes(filter)) {
        this.activeFilters = this.activeFilters.filter((f) => f !== filter);
      } else {
        this.activeFilters.push(filter);
      }

      // 如果没有筛选，默认显示全部
      if (this.activeFilters.length === 0) {
        this.activeFilters = ["all"];
      }
    },
    matchesAbilityFilter(role, filter) {
      const ability = role.ability.toLowerCase();
      const roleName = role.name;

      switch (filter) {
        case "firstNightInfo": //checked
          return ability.includes("首个夜晚") && ability.includes("你会得知");
        case "gainAbility": //checked
          return (
            ability.includes("获得") ||
            (ability.includes("拥有") &&
              (ability.includes("能力") || ability.includes("技能"))) ||
            roleName === "悟道者" // 悟道者有特殊的获得能力
          );
        case "everyNightInfo": //checked
          return (
            ability.includes("每个夜晚") &&
            ability.includes("你会得知") &&
            !ability.includes("*")
          );
        case "everyNightChoose": //checked
          return (
            ability.includes("每个夜晚") &&
            ability.includes("你要选择") &&
            !ability.includes("*")
          );
        case "limitedAbility": //checked
          return (
            (ability.includes("一次") ||
              ability.includes("限一次") ||
              ability.includes("限次") ||
              ability.includes("两次") ||
              ability.includes("三次")) &&
            roleName !== "维齐尔" // 维齐尔的能力不符合限次能力的定义
          );
        case "everyNightChooseAny": //checked
          return ability.includes("每个夜晚*") && ability.includes("你要选择");
        case "everyNightInfoAny": //checked
          return ability.includes("每个夜晚*") && ability.includes("你会得知");

        case "passiveTrigger":
          return (
            ability.includes("被") ||
            ability.includes("触发") ||
            ability.includes("当") ||
            ability.includes("如果") ||
            ability.includes("时") ||
            ability.includes("会")
          );

        case "publicTrigger":
          return ability.includes("公开") || ability.includes("宣告");
        case "visitStoryteller":
          return (
            ((ability.includes("说书人") || ability.includes("说书⼈")) && // 全角"⼈"
              (ability.includes("询问") ||
                ability.includes("拜访") ||
                ability.includes("访问"))) ||
            roleName == "渔夫"
          );
        case "deathTrigger":
          return (
            ability.includes("死") &&
            (ability.includes("被") ||
              ability.includes("触发") ||
              ability.includes("当") ||
              ability.includes("如果") ||
              ability.includes("时") ||
              ability.includes("会"))
          );
        case "specialWinLose": //checked
          return (
            (ability.includes("胜利") ||
              ability.includes("阵营失败") ||
              ability.includes("阵营获胜") ||
              ability.includes("获胜") ||
              ability.includes("胜负")) &&
            roleName !== "渔夫" // 渔夫没有特殊胜负条件
          );
        case "nomination": //checked
          return ability.includes("提名");
        case "cognitiveOverride": //checked
          return (
            ability.includes("认知") ||
            ability.includes("以为") ||
            ability.includes("觉得")
          );

        case "deathTriggerChoose":
          return (
            (ability.includes("死亡") || ability.includes("被处决")) &&
            ability.includes("选择") &&
            (ability.includes("被") ||
              ability.includes("触发") ||
              ability.includes("当") ||
              ability.includes("如果") ||
              ability.includes("时") ||
              ability.includes("会"))
          );
        case "viewGrimoire": //checked
          return ability.includes("魔典");
        case "passiveTriggerAbility":
          return (
            ability.includes("被") ||
            ability.includes("触发") ||
            ability.includes("当") ||
            ability.includes("如果") ||
            ability.includes("时") ||
            ability.includes("会")
          );

        case "everyNightChooseRole":
          return (
            ability.includes("每个夜晚") &&
            ability.includes("选择") &&
            ability.includes("角色")
          );
        case "everyNightActivate":
          return (
            (ability.includes("每个夜晚") && ability.includes("是否")) ||
            ability.includes("发动") ||
            ability.includes("使用")
          );
        case "settingsInteraction":
          return (
            ability.includes("+") ||
            ability.includes("-") ||
            ability.includes("调整") ||
            ability.includes("设置") ||
            ability.includes("互动") ||
            ability.includes("干扰") ||
            ability.includes("影响")
          );
        case "exposeRole":
          return (
            ability.includes("声明") ||
            ability.includes("公开") ||
            ability.includes("身份") ||
            ability.includes("暴露") ||
            ability.includes("角色")
          );
        default:
          return false;
      }
    },
    setFilter(filter) {
      this.activeFilter = filter;
    },
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
    applySearch(rolesGrouped) {
      if (!this.searchQuery.trim()) {
        return rolesGrouped;
      }

      const query = this.searchQuery.toLowerCase().trim();
      const filtered = {};

      Object.keys(rolesGrouped).forEach((team) => {
        const filteredRoles = rolesGrouped[team].filter((role) => {
          return (
            role.name.toLowerCase().includes(query) ||
            role.ability.toLowerCase().includes(query)
          );
        });

        if (filteredRoles.length > 0) {
          filtered[team] = filteredRoles;
        }
      });

      return filtered;
    },
    clearSearch() {
      this.searchQuery = "";
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
#townsquare.public~.characters .modal .player {
  display: none;
}

.reference-list {
  align-content: normal !important;
  align-items: normal !important;
}

.filter-tags {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin: 10px 0;
  flex-wrap: wrap;
  flex-direction: column;

  .search-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
    flex-wrap: wrap;

    .search-input {
      padding: 6px 12px;
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: rgba(255, 255, 255, 0.1);
      color: white;
      font-size: 0.9rem;
      width: 300px;
      max-width: 100%;
      outline: none;
      transition: all 0.2s ease;

      &::placeholder {
        color: rgba(255, 255, 255, 0.6);
      }

      &:focus {
        border-color: rgba(255, 255, 255, 0.6);
        background: rgba(255, 255, 255, 0.15);
        transform: scale(1.02);
      }
    }

    .clear-search {
      background: rgba(255, 99, 99, 0.2);
      border-color: #ff6363;

      &:hover {
        background: rgba(255, 99, 99, 0.3);
      }

      svg {
        margin-right: 4px;
      }
    }
  }

  .filter-row {
    display: flex;
    justify-content: center;
    gap: 4px;
    margin: 2px 0;
    flex-wrap: wrap;
  }

  .tag {
    padding: 4px 8px;
    border-radius: 12px;
    border: 1px solid transparent;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.2s ease;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    user-select: none;
    font-size: 0.85rem;
    line-height: 1.2;

    &:hover {
      background: rgba(255, 255, 255, 0.2);
      transform: translateY(-1px);
    }

    &.active {
      background: rgba(255, 255, 255, 0.3);
      border-color: white;
      transform: scale(1.02);
    }

    &.townsfolk {
      border-color: $townsfolk;

      &.active {
        background: rgba($townsfolk, 0.3);
        color: $townsfolk;
        border-color: $townsfolk;
      }
    }

    &.outsider {
      border-color: $outsider;

      &.active {
        background: rgba($outsider, 0.3);
        color: $outsider;
        border-color: $outsider;
      }
    }

    &.minion {
      border-color: $minion;

      &.active {
        background: rgba($minion, 0.3);
        color: $minion;
        border-color: $minion;
      }
    }

    &.demon {
      border-color: $demon;

      &.active {
        background: rgba($demon, 0.3);
        color: $demon;
        border-color: $demon;
      }
    }

    &.fabled {
      border-color: $fabled;

      &.active {
        background: rgba($fabled, 0.3);
        color: $fabled;
        border-color: $fabled;
      }
    }

    &.filter-toggle {
      border-color: #ffcc66;
      background: rgba(#ffcc66, 0.1);

      &.active {
        background: rgba(#ffcc66, 0.3);
        color: #ffcc66;
        border-color: #ffcc66;
      }

      svg {
        margin-right: 2px;
      }
    }

    &.ability-filter {
      border-color: #66ccff;

      &.active {
        background: rgba(#66ccff, 0.3);
        color: #66ccff;
        border-color: #66ccff;
      }
    }
  }
}
</style>