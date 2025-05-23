import Vue from "vue";
import App from "./App";
import store from "./store";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { fab } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import socketPlugin from "./store/socket";

const faIcons = [
  "AddressCard",
  "BookOpen",
  "BookDead",
  "BroadcastTower",
  "Chair",
  "CheckSquare",
  "CloudMoon",
  "Cog",
  "Copy",
  "Clipboard",
  "Dice",
  "Dragon",
  "ExchangeAlt",
  "ExclamationTriangle",
  "FileCode",
  "FileUpload",
  "HandPaper",
  "HandPointRight",
  "Heartbeat",
  "Image",
  "Link",
  "MinusCircle",
  "PeopleArrows",
  "PlusCircle",
  "Question",
  "Random",
  "RedoAlt",
  "SearchMinus",
  "SearchPlus",
  "Skull",
  "Square",
  "TheaterMasks",
  "Times",
  "TimesCircle",
  "TrashAlt",
  "Undo",
  "User",
  "UserEdit",
  "UserFriends",
  "Users",
  "VenusMars",
  "VolumeUp",
  "VolumeMute",
  "VoteYea",
  "WindowMaximize",
  "WindowMinimize",
];
const fabIcons = ["Github", "Discord"];
library.add(
  ...faIcons.map((i) => fas["fa" + i]),
  ...fabIcons.map((i) => fab["fa" + i]),
);
Vue.component("font-awesome-icon", FontAwesomeIcon);
Vue.config.productionTip = false;

// 等待 store 初始化完成后再注册 socketPlugin
store.subscribe((mutation, state) => {
  if (mutation.type === "session/setSessionId" && state.session.sessionId) {
    socketPlugin(store);
  }
});

new Vue({
  render: (h) => h(App),
  store,
}).$mount("#app");
