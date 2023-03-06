
-- Order tree nodes by how many times they occur cumulatively in test trees
SELECT name, SUM(node_frequency.frequency) AS count FROM tree_node 
    LEFT JOIN node_frequency ON tree_node.id = node_frequency.node_id 
    GROUP BY tree_node.id ORDER BY SUM(node_frequency.frequency) DESC;

-- Same as above but filter out tests that don't run with flang-new -c %s
SELECT tree_node.name, SUM(ff.frequency) FROM tree_node
    LEFT JOIN (SELECT node_frequency.id, frequency, 
        node_frequency.node_id FROM node_frequency 
        JOIN test_file ON test_file.id = node_frequency.test_id
        WHERE test_file.can_compile) ff
    ON ff.node_id = tree_node.id
    GROUP BY tree_node.id ORDER BY SUM(ff.frequency) DESC;

-- Checks number of tests per each found TODO err message
SELECT todo_message.msg, COUNT(todo_instance.id) FROM todo_message 
    JOIN todo_instance ON todo_instance.msg_id = todo_message.id 
    GROUP BY todo_message.id ORDER BY COUNT(todo_instance.id) DESC;
