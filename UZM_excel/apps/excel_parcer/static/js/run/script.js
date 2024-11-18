const allSelectors = document.querySelectorAll('.selector')
allSelectors.forEach((item, index) => {
  item.addEventListener('change', () => {
    if (item.value) {
      if (index < allSelectors.length - 1) {
        console.log(index)
        console.log(allSelectors.length)
        allSelectors[index + 1].disabled = false
      }
    }
  })
})
