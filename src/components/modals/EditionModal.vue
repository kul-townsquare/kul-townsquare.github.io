<template>
  <Modal class="editions" v-if="modals.edition" @close="toggleModal('edition')">
    <div v-if="!isCustom">
      <h3>选择剧本：</h3>
      <ul class="editions">
        <li
          v-for="edition in editions"
          class="edition"
          :class="['edition-' + edition.id]"
          :style="{
            backgroundImage: `url(${
              edition.logo
                ? edition.logo
                : require(
                    '../../assets/editions/' +
                      (edition.id || 'custom') +
                      '.png',
                  )
            })`,
          }"
          :key="edition.id"
          @click="setEdition(edition)"
        >
          {{ edition.name }}
        </li>
        <li
          class="edition edition-custom"
          @click="isCustom = true"
          :style="{
            backgroundImage: `url(${require('../../assets/editions/custom.png')})`,
          }"
        >
          导入JSON
        </li>
      </ul>
    </div>
    <div class="custom" v-else>
      <h3>从JSON加载剧本</h3>
      <!-- <h3>最近在玩的自定义剧本：</h3> -->
      <ul class="scripts">
        <li
          v-for="(script, index) in scripts"
          :key="index"
          @click="handleURL(script[1])"
        >
          {{ script[0] }}
        </li>
      </ul>
      <input
        type="file"
        ref="upload"
        accept="application/json"
        @change="handleUpload"
      />
      <div class="button-group">
        <div class="button" @click="openUpload">
          <font-awesome-icon icon="file-upload" /> 上传 JSON
        </div>
        <div class="button" @click="promptURL">
          <font-awesome-icon icon="link" /> 输入网址
        </div>
        <div class="button" @click="readFromClipboard">
          <font-awesome-icon icon="clipboard" /> 使用剪贴板中的JSON
        </div>
        <div class="button" @click="isCustom = false">
          <font-awesome-icon icon="undo" /> 返回
        </div>
      </div>
    </div>
  </Modal>
</template>

<script>
import editionJSON from "../../editions";
import { mapMutations, mapState } from "vuex";
import Modal from "./Modal";

export default {
  components: {
    Modal,
  },
  data: function () {
    return {
      editions: editionJSON,
      isCustom: false,
      scripts: [
        [
          "万圣访客",
          "https://raw.githubusercontent.com/kul-townsquare/kul-townsquare.github.io/1cf0b0fc9fb6e6c1b50c1f77e23e0d581a02a745/%E5%89%A7%E6%9C%ACJSON/2025.11/%23%E4%B8%87%E5%9C%A3%E8%AE%BF%E5%AE%A2-%E7%86%8A%E7%8C%AB%E8%83%BD%E8%83%BD%26%E6%80%A7%E6%84%9F.json",
        ],
        [
          "哎呦!猫萌特",
          "https://raw.githubusercontent.com/kul-townsquare/kul-townsquare.github.io/1cf0b0fc9fb6e6c1b50c1f77e23e0d581a02a745/%E5%89%A7%E6%9C%ACJSON/2025.11/%23%E5%93%8E%E5%91%A6!%E7%8C%AB%E8%90%8C%E7%89%B9-L%20Moment.json",
        ],
        [
          "仲夏夜之梦",
          "https://raw.githubusercontent.com/kul-townsquare/kul-townsquare.github.io/1cf0b0fc9fb6e6c1b50c1f77e23e0d581a02a745/%E5%89%A7%E6%9C%ACJSON/2025.11/%E4%BB%B2%E5%A4%8F%E5%A4%9C%E4%B9%8B%E6%A2%A6v1.1.1.json",
        ],
        [
          "圆桌骑士团",
          "https://raw.githubusercontent.com/kul-townsquare/kul-townsquare.github.io/1cf0b0fc9fb6e6c1b50c1f77e23e0d581a02a745/%E5%89%A7%E6%9C%ACJSON/2025.11/%E5%9C%86%E6%A1%8C%E9%AA%91%E5%A3%AB%E5%9B%A2v3.0.json",
        ],
        [
          "达芬奇密码",
          "https://raw.githubusercontent.com/kul-townsquare/kul-townsquare.github.io/1cf0b0fc9fb6e6c1b50c1f77e23e0d581a02a745/%E5%89%A7%E6%9C%ACJSON/2025.11/%E8%BE%BE%E8%8A%AC%E5%A5%87%E5%AF%86%E7%A0%81v1.3.2.json",
        ],
      ],
    };
  },
  computed: mapState(["modals"]),
  methods: {
    openUpload() {
      this.$refs.upload.click();
    },
    handleUpload() {
      const file = this.$refs.upload.files[0];
      if (file && file.size) {
        const reader = new FileReader();
        reader.addEventListener("load", () => {
          try {
            const roles = JSON.parse(reader.result);
            this.parseRoles(roles);
          } catch (e) {
            alert("Error reading custom script: " + e.message);
          }
          this.$refs.upload.value = "";
        });
        reader.readAsText(file);
      }
    },
    promptURL() {
      const url = prompt("输入自定义剧本json文件的url");
      if (url) {
        this.handleURL(url);
      }
    },
    convertGitHubBlobToRaw(url) {
      // 将 GitHub blob 链接转换为 raw 链接
      // 例如: github.com/user/repo/blob/branch/path → raw.githubusercontent.com/user/repo/branch/path
      const blobMatch = url.match(/github\.com\/([^/]+)\/([^/]+)\/blob\/(.+)/);
      if (blobMatch) {
        const [, owner, repo, path] = blobMatch;
        return `https://raw.githubusercontent.com/${owner}/${repo}/${path}`;
      }
      return url;
    },
    async handleURL(url) {
      try {
        // 自动转换 GitHub blob 链接为 raw 链接
        const rawUrl = this.convertGitHubBlobToRaw(url);
        
        const res = await fetch(rawUrl);
        if (!res.ok) {
          alert(`无法加载文件: ${res.status} ${res.statusText}`);
          return;
        }
        
        const script = await res.json();
        this.parseRoles(script);
      } catch (e) {
        alert("Error loading custom script: " + e.message);
      }
    },
    async readFromClipboard() {
      const text = await navigator.clipboard.readText();
      try {
        const roles = JSON.parse(text);
        this.parseRoles(roles);
      } catch (e) {
        alert("Error reading custom script: " + e.message);
      }
    },
    parseRoles(roles) {
      if (!roles || !roles.length) return;
      roles = roles.map((role) =>
        typeof role === "string" ? { id: role } : role,
      );
      const metaIndex = roles.findIndex(({ id }) => id === "_meta");
      let meta = {};
      if (metaIndex > -1) {
        meta = roles.splice(metaIndex, 1).pop();
      }
      this.$store.commit("setCustomRoles", roles);
      this.$store.commit(
        "setEdition",
        Object.assign({}, meta, { id: "custom" }),
      );
      // check for fabled and set those too, if present
      if (roles.some((role) => this.$store.state.fabled.has(role.id || role))) {
        const fabled = [];
        roles.forEach((role) => {
          if (this.$store.state.fabled.has(role.id || role)) {
            fabled.push(this.$store.state.fabled.get(role.id || role));
          }
        });
        this.$store.commit("players/setFabled", { fabled });
      }
      this.isCustom = false;
    },
    ...mapMutations(["toggleModal", "setEdition"]),
  },
};
</script>

<style scoped lang="scss">
ul.editions .edition {
  font-family: PiratesBay, sans-serif;
  letter-spacing: 1px;
  text-align: center;
  padding-top: 5%;
  background-position: center center;
  background-size: 65% auto;
  background-repeat: no-repeat;
  width: 18%;
  margin: 1px;
  font-size: 120%;
  text-shadow:
    -1px -1px 0 #000,
    1px -1px 0 #000,
    -1px 1px 0 #000,
    1px 1px 0 #000,
    0 0 5px rgba(0, 0, 0, 0.75);
  cursor: pointer;
  &:hover {
    color: red;
  }
}

.custom {
  text-align: center;
  input[type="file"] {
    display: none;
  }
  .scripts {
    list-style-type: disc;
    font-size: 120%;
    cursor: pointer;
    display: block;
    width: 50%;
    text-align: left;
    margin: 10px auto;
    li:hover {
      color: red;
    }
  }
}
</style>
