// cmdk always marks one item as selected and moves the mark on pointer move.
// Only paint it while the pointer is over the list or the keyboard is in use.
export const COMMAND_ITEM_CLASS =
  "data-selected:bg-transparent group-data-[active=true]/cmd:data-[selected=true]:bg-muted"
