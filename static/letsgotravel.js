const bucketlist = document.querySelector('#bucketlist');
const bucketlistHeader = document.querySelector('#bucketlist-header');
let countryName = '';
let bucketlistName = '';

bucketlist.addEventListener('click', function(evt) {
    if (evt.target.tagName === 'LI') {
        evt.target.classList.toggle('done');
        countryName = evt.target.innerText;
        bucketlistName = bucketlistHeader.innerText;
        completeBucketlistCountry(evt.target.className);
    }
});

async function completeBucketlistCountry(completed) {
    const resp = await axios.post(`/bucketlists/country/${countryName}/complete`, {
        bucketlist_name: bucketlistName,
        completed: completed
    });
    console.log(resp.data);
}